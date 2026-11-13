"""
Preservation property tests for the lisvap masked-array performance bugfix.

Spec: .kiro/specs/lisvap-masked-array-perf  (Task 2, Property 2: Preservation)

These tests follow the observation-first methodology: they observe the CURRENT
(unfixed, ``numpy.ma`` masked) behaviour and assert the behaviour that must be
PRESERVED by the Phase A fix. They are deliberately written so they PASS on the
unfixed masked implementation AND keep passing after Phase A, when the operators
and the read/write boundaries return plain ``float64``-with-NaN instead of
``numpy.ma`` masked arrays.

The guiding rule (design.md "Preservation Checking"): the assertions compare
finite-cell VALUES (within tolerance) and NaN/missing PLACEMENT only. They never
assert the array subtype (masked vs plain), so the representation change in
Phase A does not break them. Missing cells are extracted with
``np.ma.filled(x, np.nan)`` which is a no-op on a plain array and materialises the
mask-as-NaN on a masked array -- identical finite/NaN footprint either way.

Three groups:

1. Operator equivalence (Hypothesis-driven, Property 2 "Operator equivalence"):
   for random float64 grids with random NaN masks, each operator in
   ``utils/operators.py`` (scalar, cover, asin, acos, sqrt, maximum, ifthenelse)
   preserves finite-cell values and NaN/missing placement, taking the CURRENT
   masked output as the golden reference. Covers out-of-domain
   asin/acos/sqrt -> NaN and in-domain equality.
2. Output file metadata golden: run efas and assert the output netCDF structure
   (variables, dims, scale_factor, add_offset, valid_min/max,
   missing_value/_FillValue, packed dtype i2).
3. DEM NaN-consistency baseline: for an efas run assert each output grid's NaN
   count equals the DEM-derived count (mirrors output.py _check_nan_consistency),
   and assert ``ignore_nan_validation`` on/off behaves as today.
"""

import os

import numpy as np
import pytest
from hypothesis import given, settings as hyp_settings, HealthCheck
from hypothesis import strategies as st
from hypothesis.extra import numpy as hnp

from lisvap.utils import (
    LisSettings,
    FileNamesManager,
    CutMap,
    MaskMapMetadata,
    NetcdfMetadata,
)
from lisvap.utils.readers import loadsetclone, loadmap
from lisvap.utils import operators as ops

current_dir = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(current_dir, 'data/tests_efas.xml')

ATOL = 1e-9


# ----------------------------------------------------------------------------
# Shared helpers
# ----------------------------------------------------------------------------
def _finite_and_nan(arr):
    """Return (values_with_nan, finite_mask) for a masked OR plain array.

    ``np.ma.filled(arr, np.nan)`` is a no-op on a plain ndarray and turns masked
    cells into NaN on a MaskedArray, so the finite footprint and the finite
    values are identical regardless of the array subtype. This is what lets the
    same assertions hold before and after the Phase A representation change.
    """
    filled = np.ma.filled(np.asarray(np.ma.filled(arr, np.nan), dtype=np.float64), np.nan)
    finite = np.isfinite(filled)
    return filled, finite


def assert_same_values_and_nan(golden, candidate, atol=ATOL):
    """Assert two grids agree on finite-cell values and on NaN/missing placement."""
    g_vals, g_finite = _finite_and_nan(golden)
    c_vals, c_finite = _finite_and_nan(candidate)
    # NaN / missing placement must match exactly.
    assert np.array_equal(g_finite, c_finite), 'NaN / missing placement diverged'
    # Finite-cell values must match within tolerance.
    assert np.allclose(g_vals[g_finite], c_vals[c_finite], atol=atol, equal_nan=False), \
        'Finite-cell values diverged beyond tolerance'


def _init_singletons():
    """Initialise LisSettings / maskmap / cut extent exactly like the model does.

    Mirrors the setup in tests_masked_array_perf.py so the operator read/math
    boundaries behave as in a real run and we get a concrete maskmap shape to
    generate grids against.
    """
    settings = LisSettings(SETTINGS_PATH)
    FileNamesManager(settings.binding['PathOut'])
    loadsetclone('MaskMap')
    file_manager = FileNamesManager.instance()
    meteo_map = file_manager.get_file_name('TMinMaps')
    CutMap.register(meteo_map)
    NetcdfMetadata.register(meteo_map)
    return settings


# ============================================================================
# Group 1 - Operator equivalence (Hypothesis)  [Requirements 3.1, 3.2, 3.7]
# ============================================================================
class TestOperatorPreservation(object):
    """Property 2: operators preserve finite values and NaN placement.

    **Validates: Requirements 3.1, 3.2, 3.7**
    """

    @classmethod
    def setup_class(cls):
        cls.settings = _init_singletons()
        cls.maskmap = MaskMapMetadata.instance().get_maskmap()
        cls.shape = cls.maskmap.shape
        # Base mask of cells excluded from modelling (missing in every grid).
        cls.base_mask = np.ma.getmaskarray(cls.maskmap)

    # -- generators ----------------------------------------------------------
    def _grid_strategy(self, min_value=-1000.0, max_value=1000.0):
        """A flat float64 array matching the maskmap size, with random NaNs.

        scalar()/operators flatten+reshape to the maskmap shape, so a flat array
        of the right size is the natural input. We draw a per-cell boolean mask
        (same size as the grid) and set those cells to NaN, so the input domain
        includes mixed finite/NaN patterns and all-missing rows. Drawing the NaN
        mask as a boolean ``hnp.arrays`` keeps the generator O(size) and within
        Hypothesis' buffer, unlike sampling a unique index list of size up to
        ``0.6 * size`` (which blows past the engine's limit at this grid size).
        """
        size = int(np.prod(self.shape))
        elements = st.floats(
            min_value=min_value, max_value=max_value,
            allow_nan=False, allow_infinity=False, width=64,
        )
        base = hnp.arrays(dtype=np.float64, shape=(size,), elements=elements)
        # Per-cell NaN mask. fill=False (mostly finite) with a sprinkling of True
        # so most draws are predominantly finite but still exercise NaN cells;
        # all-True / all-False extremes remain reachable.
        nan_mask = hnp.arrays(
            dtype=np.bool_, shape=(size,),
            elements=st.booleans(), fill=st.just(False),
        )
        return st.tuples(base, nan_mask)

    @staticmethod
    def _inject_nans(flat, nan_mask):
        flat = flat.copy()
        flat[nan_mask] = np.nan
        return flat

    # -- scalar --------------------------------------------------------------
    @hyp_settings(max_examples=40, deadline=None,
                  suppress_health_check=[HealthCheck.data_too_large])
    @given(st.data())
    def test_scalar_preserves_values_and_mask(self, data):
        flat, nan_mask = data.draw(self._grid_strategy())
        flat = self._inject_nans(flat, nan_mask)

        result = ops.scalar(flat)

        # Expected: values reshaped to maskmap shape, NaN where the maskmap masks.
        expected = flat.reshape(self.shape).astype(np.float64).copy()
        expected[self.base_mask] = np.nan

        assert result.shape == self.shape
        assert_same_values_and_nan(expected, result)

    @hyp_settings(max_examples=25, deadline=None)
    @given(value=st.floats(min_value=-500.0, max_value=500.0,
                           allow_nan=False, allow_infinity=False))
    def test_scalar_constant_fills_unmasked_cells(self, value):
        result = ops.scalar(value)
        vals, finite = _finite_and_nan(result)
        # Every finite (unmasked) cell carries the constant.
        assert np.allclose(vals[finite], value, atol=ATOL)
        # NaN exactly on the structural maskmap mask.
        assert np.array_equal(~finite, self.base_mask)

    # -- cover ---------------------------------------------------------------
    @hyp_settings(max_examples=40, deadline=None,
                  suppress_health_check=[HealthCheck.data_too_large])
    @given(st.data())
    def test_cover_fills_nan_with_mv(self, data):
        flat, nan_mask = data.draw(self._grid_strategy())
        flat = self._inject_nans(flat, nan_mask)
        mv = data.draw(st.floats(min_value=-10.0, max_value=10.0,
                                 allow_nan=False, allow_infinity=False))

        result = ops.cover(flat, mv)
        res_vals = np.ma.filled(np.asarray(np.ma.filled(result, np.nan), dtype=np.float64), np.nan)

        # Golden observation of current behaviour: cover() replaces EVERY NaN in
        # the scalar() view (structural mask + injected NaNs) with mv, so the
        # underlying data has no NaN left. We assert that data footprint, which
        # is representation independent.
        scal = ops.scalar(flat)
        scal_filled = np.ma.filled(np.asarray(np.ma.filled(scal, np.nan), dtype=np.float64), np.nan)
        expected = scal_filled.copy()
        expected[np.isnan(expected)] = mv

        assert np.allclose(res_vals, expected, atol=ATOL, equal_nan=True)

    # -- sqrt ----------------------------------------------------------------
    @hyp_settings(max_examples=40, deadline=None,
                  suppress_health_check=[HealthCheck.data_too_large])
    @given(st.data())
    def test_sqrt_in_and_out_of_domain(self, data):
        # Range spans negatives (out of domain -> NaN) and positives (in domain).
        flat, nan_mask = data.draw(self._grid_strategy(min_value=-50.0, max_value=50.0))
        flat = self._inject_nans(flat, nan_mask)
        grid = flat.reshape(self.shape)

        result = ops.sqrt(grid)
        res_vals, res_finite = _finite_and_nan(result)

        in_domain = grid >= 0
        was_nan = np.isnan(grid)
        # Out-of-domain (negative) and originally-NaN cells -> NaN.
        assert not np.any(res_finite[~in_domain]), 'negative/NaN inputs must map to NaN'
        # In-domain finite cells equal sqrt of the input (within rounding).
        good = in_domain & ~was_nan
        assert np.allclose(res_vals[good], np.sqrt(grid[good]), atol=1e-6)

    # -- asin / acos ---------------------------------------------------------
    @hyp_settings(max_examples=40, deadline=None,
                  suppress_health_check=[HealthCheck.data_too_large])
    @given(st.data())
    def test_asin_in_and_out_of_domain(self, data):
        self._check_inverse_trig(data, ops.asin, np.arcsin)

    @hyp_settings(max_examples=40, deadline=None,
                  suppress_health_check=[HealthCheck.data_too_large])
    @given(st.data())
    def test_acos_in_and_out_of_domain(self, data):
        self._check_inverse_trig(data, ops.acos, np.arccos)

    def _check_inverse_trig(self, data, op, ref_fn):
        # Range deliberately exceeds [-1, 1] so out-of-domain -> NaN is exercised.
        flat, nan_mask = data.draw(self._grid_strategy(min_value=-3.0, max_value=3.0))
        flat = self._inject_nans(flat, nan_mask)
        grid = flat.reshape(self.shape)

        result = op(grid, in_degrees=True, positive_angles=True)
        res_vals, res_finite = _finite_and_nan(result)

        in_domain = (grid >= -1) & (grid <= 1)
        was_nan = np.isnan(grid)
        # Out-of-domain and NaN inputs map to NaN.
        assert not np.any(res_finite[~in_domain | was_nan]), \
            'out-of-domain / NaN inputs must map to NaN'
        # In-domain cells: positive angles in degrees, matching the pcraster-compat path.
        good = in_domain & ~was_nan
        angle = ref_fn(grid[good])
        angle = np.where(angle < 0.0, angle + 2 * np.pi, angle)
        expected_deg = np.rad2deg(angle)
        assert np.allclose(res_vals[good], expected_deg, atol=1e-6)

    # -- maximum -------------------------------------------------------------
    @hyp_settings(max_examples=40, deadline=None,
                  suppress_health_check=[HealthCheck.data_too_large])
    @given(st.data())
    def test_maximum_preserves_values_and_nan(self, data):
        flat_a, nan_a = data.draw(self._grid_strategy())
        flat_b, nan_b = data.draw(self._grid_strategy())
        a = ops.scalar(self._inject_nans(flat_a, nan_a))
        b = ops.scalar(self._inject_nans(flat_b, nan_b))

        result = ops.maximum(a, b)

        a_vals, _ = _finite_and_nan(a)
        b_vals, _ = _finite_and_nan(b)
        expected = np.maximum(a_vals, b_vals)  # NaN propagates in either operand
        assert_same_values_and_nan(expected, result)

    # -- ifthenelse (np.where) ----------------------------------------------
    @hyp_settings(max_examples=40, deadline=None,
                  suppress_health_check=[HealthCheck.data_too_large])
    @given(st.data())
    def test_ifthenelse_preserves_values_and_nan(self, data):
        flat_a, nan_a = data.draw(self._grid_strategy())
        flat_b, nan_b = data.draw(self._grid_strategy())
        a = ops.scalar(self._inject_nans(flat_a, nan_a))
        b = ops.scalar(self._inject_nans(flat_b, nan_b))

        a_vals, _ = _finite_and_nan(a)
        b_vals, _ = _finite_and_nan(b)
        cond = a_vals > b_vals  # NaN compares False -> picks b branch

        result = ops.ifthenelse(cond, a, b)
        expected = np.where(cond, a_vals, b_vals)
        assert_same_values_and_nan(expected, result)


# ============================================================================
# Group 2 + 3 - Output metadata golden & DEM NaN-consistency baseline
# ============================================================================
class TestOutputPreservation(object):
    """Run efas once; assert file-metadata golden and DEM NaN-consistency.

    **Validates: Requirements 3.1, 3.3, 3.4, 3.6**
    """

    # Golden metadata observed on the unfixed code (per-variable scale_factor /
    # valid ranges come straight from defaults_options.ReportedMap).
    EXPECTED_META = {
        'e0': dict(standard_name='water_potential_evaporation_flux',
                   scale_factor=0.01, add_offset=0.0,
                   valid_min=0, valid_max=5000, missing_value=-9999),
        'es': dict(standard_name='water_evaporation_flux_from_soil',
                   scale_factor=0.01, add_offset=0.0,
                   valid_min=0, valid_max=5000, missing_value=-9999),
        'et': dict(standard_name='water_evapotranspiration_flux',
                   scale_factor=0.01, add_offset=0.0,
                   valid_min=0, valid_max=5000, missing_value=-9999),
        'tair': dict(standard_name='air_temperature',
                     scale_factor=0.1, add_offset=0.0,
                     valid_min=-600, valid_max=600, missing_value=-9999),
    }

    @classmethod
    def setup_class(cls):
        from netCDF4 import Dataset  # local import keeps module import light
        cls.Dataset = Dataset
        # LisSettings is a Singleton keyed by the settings-file path. When an earlier test
        # module (e.g. tests_efas.py) already ran this exact settings file, its lisvapexe call
        # mutated the cached binding in place (StepStart/StepEnd/CalendarDayStart get converted
        # from date strings to integer step numbers), so reusing the cached instance here would
        # feed ints into strptime. Evict the cached instance so the binding is parsed fresh from
        # the XML, matching a clean-process run. (Isolation fix only; no assertion changes.)
        from lisvap.utils import Singleton
        Singleton._instances = {
            k: v for k, v in Singleton._instances.items()
            if not (isinstance(k, tuple) and k and k[0] is LisSettings)
        }
        Singleton._current.pop(LisSettings, None)
        cls.settings = LisSettings(SETTINGS_PATH)
        cls.output_path = cls.settings.binding['PathOut']
        # The model entry point (lisvapexe -> setup_calendar) expects a FileNamesManager
        # singleton to already exist (tests_efas.py constructs it the same way before the run).
        FileNamesManager(cls.output_path)
        # Fresh run so the golden is produced by THIS code, not a stale artifact.
        for var in ('e0', 'es', 'et', 'tair'):
            p = os.path.join(cls.output_path, var + '.nc')
            if os.path.exists(p):
                os.remove(p)
        from lisvap1 import lisvapexe
        from lisvap.utils import cdf_flags
        cdf_flags['all'] = 0
        cdf_flags['steps'] = 0
        cdf_flags['end'] = 0
        assert cls.settings.valid(), 'efas settings did not validate'
        lisvapexe(cls.settings)

    @classmethod
    def teardown_class(cls):
        from lisvap.utils import cdf_flags
        cdf_flags['all'] = 0
        cdf_flags['steps'] = 0
        cdf_flags['end'] = 0

    # -- Group 2: file metadata golden --------------------------------------
    @pytest.mark.parametrize('var', ['e0', 'es', 'et', 'tair'])
    def test_output_metadata_golden(self, var):
        path = os.path.join(self.output_path, var + '.nc')
        assert os.path.exists(path), 'expected output file {}'.format(path)
        ds = self.Dataset(path, 'r')
        try:
            # Structure: spatial + time dims and the expected variables present.
            assert set(ds.dimensions) == {'x', 'y', 'time'}
            assert var in ds.variables
            for coord in ('x', 'y', 'time'):
                assert coord in ds.variables

            v = ds.variables[var]
            # Packed dtype is int16 (i2).
            assert v.dtype == np.dtype('int16')
            assert v.dimensions == ('time', 'y', 'x')

            exp = self.EXPECTED_META[var]
            assert v.standard_name == exp['standard_name']
            assert float(v.scale_factor) == pytest.approx(exp['scale_factor'])
            assert float(v.add_offset) == pytest.approx(exp['add_offset'])
            assert int(v.valid_min) == exp['valid_min']
            assert int(v.valid_max) == exp['valid_max']
            assert int(v.missing_value) == exp['missing_value']
            assert int(v._FillValue) == exp['missing_value']
        finally:
            ds.close()

    # -- Group 3: DEM NaN-consistency baseline ------------------------------
    def test_dem_nan_consistency_baseline(self):
        """Every output grid's NaN count equals the DEM-derived NaN count.

        Mirrors output.py::_check_nan_consistency against the SAME DEM the model
        used, independent of the array subtype.
        """
        # Re-init singletons for this settings instance and load the DEM the way
        # the model does (loadmap -> masked in the cut domain today, NaN cells).
        LisSettings(SETTINGS_PATH)
        FileNamesManager(self.output_path)
        loadsetclone('MaskMap')
        file_manager = FileNamesManager.instance()
        meteo_map = file_manager.get_file_name('TMinMaps')
        CutMap.register(meteo_map)
        NetcdfMetadata.register(meteo_map)

        dem = loadmap('Dem')
        dem_filled = np.ma.filled(np.asarray(np.ma.filled(dem, np.nan), dtype=np.float64), np.nan)
        dem_nan = int(np.count_nonzero(np.isnan(dem_filled)))
        assert dem_nan > 0, 'DEM should have masked/NaN cells in the EFAS domain'

        for var in ('e0', 'es', 'et'):
            path = os.path.join(self.output_path, var + '.nc')
            ds = self.Dataset(path, 'r')
            try:
                v = ds.variables[var]
                v.set_auto_maskandscale(True)
                nsteps = v.shape[0]
                for step in range(nsteps):
                    grid = v[step, :, :]
                    grid_filled = np.ma.filled(np.asarray(np.ma.filled(grid, np.nan),
                                                          dtype=np.float64), np.nan)
                    out_nan = int(np.count_nonzero(np.isnan(grid_filled)))
                    assert out_nan == dem_nan, (
                        'NaN consistency: var {} step {} has {} NaN cells, '
                        'DEM has {}'.format(var, step, out_nan, dem_nan))
            finally:
                ds.close()

    def test_ignore_nan_validation_toggle_behaviour(self):
        """ignore_nan_validation on -> NaN check skipped; off -> check runs.

        Observes the OutputMap.initial() wiring exactly as today: the
        ``_validate_nan`` flag is the negation of the option, and the DEM NaN
        count is only computed when validation is on.
        """
        from lisvap.utils.output import OutputMap

        class _Var(object):
            pass

        # OFF (default): validation active, DEM NaN count computed.
        s_off = LisSettings(SETTINGS_PATH)
        FileNamesManager(s_off.binding['PathOut'])
        loadsetclone('MaskMap')
        fm = FileNamesManager.instance()
        meteo_map = fm.get_file_name('TMinMaps')
        CutMap.register(meteo_map)
        NetcdfMetadata.register(meteo_map)

        var_off = _Var()
        var_off.settings = s_off
        var_off.Dem = loadmap('Dem')
        om_off = OutputMap(var_off)
        om_off.initial()
        assert om_off._validate_nan is True
        assert hasattr(om_off, '_dem_nan_count') and om_off._dem_nan_count > 0

        # ON: validation skipped, no DEM NaN count computed.
        assert s_off.get_option('ignore_nan_validation') is False
        var_on = _Var()

        class _SettingsIgnore(object):
            def __init__(self, inner):
                self._inner = inner

            def get_option(self, key):
                if key == 'ignore_nan_validation':
                    return True
                return self._inner.get_option(key)

        var_on.settings = _SettingsIgnore(s_off)
        var_on.Dem = loadmap('Dem')
        om_on = OutputMap(var_on)
        om_on.initial()
        assert om_on._validate_nan is False
        assert not hasattr(om_on, '_dem_nan_count')
