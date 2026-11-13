"""
Expected-behavior exploration test for the lisvap masked-array performance fix.

Spec: .kiro/specs/lisvap-masked-array-perf  (Task 1 / Property 1: Expected Behavior)

This test documents the FIXED behavior after the Phase A de-masking. Since the
"Remove pcraster" migration every grid used to be a ``numpy.ma`` masked array and
those masked arrays were carried through the entire per-timestep computation (mask
propagation / defensive copies / Python-level ``numpy.ma`` operator wrappers dominated
the runtime).

Phase A changed the in-memory representation: grids are now plain ``numpy.ndarray``
``float64`` arrays that use NaN for missing cells. The mask is applied exactly once at
the read boundary (``readnetcdf``), the constructors (``scalar``/``cover``) build plain
arrays, and the per-timestep math stays on plain ndarrays.

    Expected_Behavior:
        isPlainFloat64(result) AND missingCellsAreNaN(result)
        AND numericallyEquivalentToOriginal(result, tolerance=reference_atol)

This is the post-fix counterpart of the original Task 1 bug-condition test: every
assertion that used to require a ``numpy.ma.MaskedArray`` now asserts the fixed
representation -- a plain ``numpy.ndarray`` of dtype ``float64`` with NaN in exactly the
masked cells and finite values elsewhere. The reference-comparison suite remains the
equivalence oracle that proves the numerics are unchanged.

The test is driven by the small ``tests_efas.xml`` domain so it stays fast and
self-contained while still exercising the real read/math boundary (readnetcdf,
scalar, cover, and a concrete penman-monteith / ESat style hot-path expression).
"""

import os

import numpy as np

from lisvap.utils import LisSettings, FileNamesManager, CutMap, MaskMapMetadata, NetcdfMetadata
from lisvap.utils.readers import loadsetclone, readnetcdf
from lisvap.utils.operators import scalar, cover, exp

current_dir = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(current_dir, 'data/tests_efas.xml')


def _mask_bool(shape):
    """Return ``maskmap.mask`` as a boolean array broadcast to ``shape``.

    For small domains numpy may collapse the mask to the scalar ``nomask``
    (a 0-d ``False``); broadcasting makes the per-cell masked-cell check work
    uniformly whether the mask is scalar or a full grid. In those domains the
    missing cells come from the source netCDF NaNs rather than from the maskmap
    mask, so the missing-cell oracle is the NaN pattern itself.
    """
    mask = np.ma.getmaskarray(np.ma.array(np.empty(shape), mask=MaskMapMetadata.instance().get_maskmap().mask))
    return np.broadcast_to(mask, shape)


class TestMaskedArrayExpectedBehavior(object):
    """Property 1 - Expected Behavior: the hot path computes on plain float64 with NaN."""

    @classmethod
    def setup_class(cls):
        # Initialise the singletons the same way LisvapModelIni does, without running
        # the full dynamic model. This gives us a real maskmap / cut extent so the
        # read and operator boundaries behave exactly as they do in a real run.
        cls.settings = LisSettings(SETTINGS_PATH)
        FileNamesManager(cls.settings.binding['PathOut'])
        loadsetclone('MaskMap')
        file_manager = FileNamesManager.instance()
        meteo_map = file_manager.get_file_name('TMinMaps')
        CutMap.register(meteo_map)
        NetcdfMetadata.register(meteo_map)
        # Timestep to read: the first simulation step (StepStart). readnetcdf resolves
        # a date string to the matching netCDF index via get_current_date/calendar.
        cls.step = cls.settings.binding['StepStart']

    # ------------------------------------------------------------------
    # Expected Behavior 1: plain-float64 read boundary (readnetcdf / loadmap)
    # ------------------------------------------------------------------
    def test_readnetcdf_returns_plain_float64_with_nan(self):
        tmin = readnetcdf(self.settings.binding['TMinMaps'], self.step,
                          variable_binding='TMinMaps')
        maskmap = MaskMapMetadata.instance().get_maskmap()
        # EXPECTED BEHAVIOR: readnetcdf returns a plain ndarray (NOT a masked array),
        # dtype float64, shaped like the maskmap.
        assert isinstance(tmin, np.ndarray), (
            'EXPECTED BEHAVIOR: readnetcdf must return a plain numpy.ndarray on the '
            'fixed code. Got {}'.format(type(tmin))
        )
        assert not isinstance(tmin, np.ma.MaskedArray), (
            'EXPECTED BEHAVIOR: readnetcdf must NOT return a numpy.ma.MaskedArray on '
            'the fixed code (masked-at-read replaced by NaN-at-read).'
        )
        assert tmin.dtype == np.float64
        assert tmin.shape == maskmap.shape
        # Missing cells are NaN: every maskmap-masked cell is NaN, and (since the mask
        # is applied exactly once at read) the overall missing-cell set carries NaN.
        missing = _mask_bool(tmin.shape)
        assert np.isnan(tmin[missing]).all(), (
            'EXPECTED BEHAVIOR: maskmap-masked cells must be NaN in the plain float64 '
            'grid.'
        )
        nan_cells = np.isnan(tmin)
        # The grid must carry a real missing-cell footprint and real modelled values
        # (not a degenerate all-NaN / all-finite grid), so the assertion is meaningful.
        assert nan_cells.any(), (
            'EXPECTED BEHAVIOR: missing cells must be represented as NaN.'
        )
        assert np.isfinite(tmin[~nan_cells]).all(), (
            'EXPECTED BEHAVIOR: non-missing cells must be finite plain float64 values.'
        )
        assert (~nan_cells).any(), (
            'EXPECTED BEHAVIOR: modelled (non-missing) cells must be present.'
        )

    # ------------------------------------------------------------------
    # Expected Behavior 2: plain-float64 constructors (scalar / cover)
    # ------------------------------------------------------------------
    def test_scalar_constructor_returns_plain_float64_with_nan(self):
        s = scalar(24.)
        maskmap = MaskMapMetadata.instance().get_maskmap()
        # EXPECTED BEHAVIOR: scalar(24.) builds a plain float64 ndarray, not masked.
        assert isinstance(s, np.ndarray), (
            'EXPECTED BEHAVIOR: scalar(24.) must return a plain numpy.ndarray on the '
            'fixed code. Got {}'.format(type(s))
        )
        assert not isinstance(s, np.ma.MaskedArray), (
            'EXPECTED BEHAVIOR: scalar(24.) must NOT return a numpy.ma.MaskedArray.'
        )
        assert s.dtype == np.float64
        assert s.shape == maskmap.shape
        # scalar() applies the maskmap mask as NaN: masked cells are NaN, every other
        # cell carries the constant value.
        missing = _mask_bool(s.shape)
        assert np.isnan(s[missing]).all(), (
            'EXPECTED BEHAVIOR: maskmap-masked cells must be NaN in scalar(24.).'
        )
        assert np.all(s[~missing] == 24.), (
            'EXPECTED BEHAVIOR: non-masked cells must carry the constant 24.'
        )

    def test_cover_constructor_returns_plain_float64_without_nan(self):
        tmin = readnetcdf(self.settings.binding['TMinMaps'], self.step,
                          variable_binding='TMinMaps')
        c = cover(tmin, 0.0)
        maskmap = MaskMapMetadata.instance().get_maskmap()
        # EXPECTED BEHAVIOR: cover(...) returns a plain float64 ndarray, not masked,
        # and fills every NaN (incl. masked cells) with mv -> no NaN remains.
        assert isinstance(c, np.ndarray), (
            'EXPECTED BEHAVIOR: cover(...) must return a plain numpy.ndarray on the '
            'fixed code. Got {}'.format(type(c))
        )
        assert not isinstance(c, np.ma.MaskedArray), (
            'EXPECTED BEHAVIOR: cover(...) must NOT return a numpy.ma.MaskedArray.'
        )
        assert c.dtype == np.float64
        assert c.shape == maskmap.shape
        assert not np.isnan(c).any(), (
            'EXPECTED BEHAVIOR: cover must fill all NaN with mv -> no NaN remains.'
        )

    # ------------------------------------------------------------------
    # Expected Behavior 3: plain-float64 per-timestep hot-path grid
    # ------------------------------------------------------------------
    def test_hot_path_grid_is_plain_float64_with_nan(self):
        """A concrete per-timestep computation stays a plain float64 array with NaN.

        Reproduces the readmeteo / penman-monteith hot path on the real read
        boundary: TAvg from TMin/TMax, then the saturated-vapour-pressure ESat and
        the ET0-style ratio. On the fixed code every intermediate and the final grid
        is a plain numpy.ndarray (NOT numpy.ma) because the inputs enter as plain
        float64-with-NaN at readnetcdf; NaN is preserved at the masked cells.
        """
        tmin = readnetcdf(self.settings.binding['TMinMaps'], self.step,
                          variable_binding='TMinMaps')
        tmax = readnetcdf(self.settings.binding['TMaxMaps'], self.step,
                          variable_binding='TMaxMaps')
        eact = readnetcdf(self.settings.binding['EActMaps'], self.step,
                          variable_binding='EActMaps', negative_value_substitute=0.0)

        # TAvg and ESat exactly as in hydrological/readmeteo.py
        t_avg = 0.5 * (tmin + tmax)
        e_sat = 6.10588 * exp((17.32491 * t_avg) / (t_avg + 238.102))

        # Penman-Monteith style ratio (same algebraic form as self.ETRef in
        # lisvapdynamic.py): ((Delta * RNA) + (Psychro * EA)) / (Delta + Psychro)
        delta = (e_sat * 4098.0) / ((t_avg + 237.3) ** 2)
        psychro = scalar(0.067)
        et_ref = ((delta * e_sat) + (psychro * eact)) / (delta + psychro)

        maskmap = MaskMapMetadata.instance().get_maskmap()
        missing = _mask_bool(tmin.shape)
        # The missing-cell footprint the math must preserve: maskmap-masked cells plus
        # the source-NaN cells that entered at the read boundary.
        input_nan = np.isnan(tmin) | np.isnan(tmax)

        for name, grid in (('TAvg', t_avg), ('ESat', e_sat), ('ET0', et_ref)):
            # EXPECTED BEHAVIOR: each hot-path grid is a plain ndarray, not masked.
            assert isinstance(grid, np.ndarray), (
                'EXPECTED BEHAVIOR: {} (hot-path grid) must be a plain numpy.ndarray '
                'on the fixed code. Got {}'.format(name, type(grid))
            )
            assert not isinstance(grid, np.ma.MaskedArray), (
                'EXPECTED BEHAVIOR: {} (hot-path grid) must NOT be a '
                'numpy.ma.MaskedArray on the fixed code (masked-in-math '
                'eliminated).'.format(name)
            )
            assert grid.dtype == np.float64, (
                'EXPECTED BEHAVIOR: {} must stay float64.'.format(name)
            )
            assert grid.shape == tmin.shape
            # NaN is preserved through the math in exactly the maskmap-masked cells and
            # in the input-missing cells (NaN propagates through plain arithmetic).
            assert np.isnan(grid[missing]).all(), (
                'EXPECTED BEHAVIOR: {} must keep NaN in the maskmap-masked '
                'cells.'.format(name)
            )
            assert np.isnan(grid[input_nan]).all(), (
                'EXPECTED BEHAVIOR: {} must keep NaN where the inputs were '
                'missing.'.format(name)
            )
            # Modelled cells (finite inputs) stay finite plain float64 values.
            assert np.isfinite(grid[~input_nan]).all(), (
                'EXPECTED BEHAVIOR: {} must be finite in the modelled '
                'cells.'.format(name)
            )
            assert (~input_nan).any(), (
                'EXPECTED BEHAVIOR: {} must have modelled (finite) '
                'cells.'.format(name)
            )
