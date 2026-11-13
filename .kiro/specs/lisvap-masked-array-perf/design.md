# Lisvap Masked-Array Performance Bugfix Design

## Overview

Since the v1.4.0 "Remove pcraster" migration, Lisvap represents every grid as a
`numpy.ma` masked array and carries those masked arrays through the entire per-timestep
computation. Mask propagation, defensive copies, and the Python-level `numpy.ma` operator
wrappers dominate the runtime: profiling the EFAS 1arcmin case (2970x4530 = 13.45M cells,
~45% masked, 11 timesteps) measured ~106 s wall-clock, of which roughly 55-70 s is
masked-array overhead rather than arithmetic. A micro-benchmark at the real grid size
showed the core operations run 1.6x-8.4x faster on plain `float64` arrays that use NaN for
missing values.

The fix changes the in-memory representation of grids, not the numerics. Grids become plain
`float64` arrays carrying NaN in missing cells. The mask is applied exactly once at read
time (when data enters the model) and the fill/mask is re-materialized exactly once at write
time (when data leaves to netCDF). The per-timestep math in `lisvapdynamic.py` and
`hydrological/readmeteo.py` then runs on plain ndarrays, and the `numpy.ma` machinery drops
out of the hot path.

The change is sequenced in two phases, strictly ordered by impact and correctness risk:

1. **Phase A - De-masking the hot path (primary, correctness-critical).** Convert the read
   boundary, the operator layer, and the write boundary so the computation runs on
   `float64`-with-NaN. This is where the ~55-70 s lives and where behavior must be proven
   equivalent against the reference outputs.
2. **Phase B - Per-timestep I/O optimizations (secondary, independent).** Keep the output
   netCDF handle open across timesteps, lower/remove `zlib` compression, and cache the time
   axis per open input file. These address the ~15 s reopen/close and ~18 s time-axis
   re-read overheads without altering output file structure, metadata, scaling, or fill
   values.

The implementation must stay numpy-based (no return to pcraster) and must keep output
numerically equivalent to the current implementation as validated against
`tests/data/reference` and the per-timestep NaN-consistency check in `utils/output.py`.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the defect - a per-timestep grid
  computation (evapotranspiration, radiation, Hargreaves, meteo derivation) is carried on
  `numpy.ma` masked arrays, incurring mask-propagation/defensive-copy/operator-wrapper
  overhead instead of running as plain `float64` arithmetic.
- **Property (P)**: The desired behavior - the same computation runs on plain `float64`
  arrays using NaN for missing cells, producing numerically equivalent results while
  eliminating the masked-array overhead.
- **Preservation**: Behavior that must remain unchanged by the fix - numerical output
  values (within the reference test tolerance), the location and count of missing cells
  (NaN-consistency against the DEM), output netCDF structure/metadata/scaling/fill values,
  the `ignore_nan_validation` setting, calendar/split-I/O/unit-conversion/6-hourly/Hargreaves
  behaviors, and the no-pcraster constraint.
- **Mask / missing cell**: A cell excluded from modelling. Today it is represented by
  `maskmap.mask == True` and `np.ma` masking; after the fix it is represented by `NaN` in a
  plain `float64` array, with the mask re-applied only at write time.
- **readnetcdf / loadmap** (`utils/readers.py`): The read boundary. Today each returns
  `np.ma.masked_array(mapnp.flatten().reshape(maskmap.shape), mask=maskmap.mask, ...)`. This
  is where data becomes masked.
- **scalar / cover** (`utils/operators.py`): Constructors that currently build masked arrays
  from scalars or ndarrays and are called throughout the radiation/angot math.
- **writenet** (`utils/writers.py`): The write boundary. Today it calls
  `inputmap.filled(np.nan)[slices]`, expecting a masked array.
- **_check_nan_consistency** (`utils/output.py`): Per-timestep validation that the NaN count
  in an output grid equals the NaN count derived from the DEM.
- **Hot path**: `evapotranspiration_using_penman_monteith`, `angot_radiation`,
  `net_absorbed_radiation`, `int_solar_height_main`/`int_solar_height_north_pole`,
  `evapotranspiration_using_hargreaves`, `latent_heat_vaporization`
  (`lisvapdynamic.py`), plus the meteo derivations in `hydrological/readmeteo.py`
  (`ESat`, `EAct`, `Wind` corrections).

## Bug Details

### Bug Condition

The bug manifests whenever a per-timestep grid computation runs on data that originated from
`readnetcdf`/`loadmap`/`scalar`/`cover` and therefore flows through the pipeline as a
`numpy.ma` masked array. The computation is either (a) propagating masks cell-by-cell through
every arithmetic operation, (b) making defensive copies inside the `numpy.ma` operator
wrappers, or (c) dispatching through the Python-level `numpy.ma` layer instead of compiled
ndarray ufuncs - all of which add overhead that is not actual arithmetic.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type Grid (a per-timestep model array)
  OUTPUT: boolean

  RETURN isMaskedArray(input)                      # type is numpy.ma.MaskedArray
         AND flowsThroughPerTimestepMath(input)    # consumed by the hot path
         AND NOT computedAsPlainFloat64WithNaN(input)
END FUNCTION
```

The property that must hold after the fix (what "fixed" means for a buggy input):

```
FUNCTION expectedBehavior(result)
  INPUT: result produced by the fixed per-timestep computation
  OUTPUT: boolean

  RETURN isPlainFloat64(result)                    # not numpy.ma
         AND missingCellsAreNaN(result)            # NaN where the mask is True
         AND numericallyEquivalentToOriginal(result, tolerance=reference_atol)
END FUNCTION
```

### Examples

- `readnetcdf('tair', t)` currently returns a `np.ma.masked_array`; the downstream
  `ESat = 6.10588 * exp((17.32491 * TAvg) / (TAvg + 238.102))` runs through `np.ma`
  wrappers. Expected: `readnetcdf` returns `float64`-with-NaN and `ESat` is a plain
  ndarray with identical finite values and NaN in the masked cells.
- `self.ETRef = ((Delta * RNA) + (Psychro * EA)) / (Delta + Psychro)` currently produces a
  masked array (dozens of masked intermediates). Expected: the same expression on plain
  arrays yields identical finite values; masked cells are NaN and propagate as NaN.
- `scalar(24.)` currently builds a masked array of 24 with the maskmap mask. Expected: a
  plain `float64` full array of 24 with NaN where the mask is True.
- `cover(day_length, mv=0.0)` currently fills NaN with 0 and re-wraps as masked. Expected:
  fills NaN with 0 on a plain array (and, where the original masked those cells, the
  mask-as-NaN is re-applied by the caller/boundary as today).
- Edge case: `asin`/`acos`/`sqrt` out-of-domain inputs map to NaN today and must continue to
  map to NaN on plain arrays; a fully-missing row at high latitude in `angot_radiation` must
  still resolve to the same covered value.

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Output values stay numerically equivalent to the current implementation, within the
  existing reference-test tolerance (`atol=0.01`, with the per-step percentage-wrong gates in
  `tests/__init__.py`).
- The count and location of missing cells in every output grid stay identical, so the
  per-timestep NaN-consistency check against the DEM in `utils/output.py` keeps holding.
- Output netCDF files keep the same structure, variables, dimensions, metadata,
  scale_factor/add_offset, valid_min/valid_max, `missing_value`/`_FillValue`, and packing.
- The `ignore_nan_validation` setting keeps being honored exactly as today.
- pcraster is not reintroduced; the implementation stays numpy-based.
- Non-hot-path behavior keeps working: settings parsing, calendar/date handling (including
  360_day and no_leap), split input/output, unit conversion, 6-hourly output, and the
  Hargreaves-vs-Penman-Monteith selection.

**Scope:**
All behavior that does NOT depend on the in-memory grid representation must be completely
unaffected by this fix. This includes:
- The numerical formulas in `lisvapdynamic.py` and `hydrological/readmeteo.py` (unchanged).
- The netCDF read/parse logic for selecting the correct timestep, applying unit conversion,
  and substituting negative values.
- The output packing (`filled(nan) -> scale -> int16`) and all file metadata.

Note: the correct behavior for buggy inputs (plain `float64` with NaN, numerically
equivalent) is defined in Property 1 below. This section captures what must NOT change.

## Hypothesized Root Cause

The root cause is confirmed by profiling, not merely hypothesized: the masked-array
representation is the dominant cost. The specific mechanisms are:

1. **Masked representation created at the read boundary**: `readnetcdf` and `loadmap` wrap
   every grid as `np.ma.masked_array(..., mask=maskmap.mask)`. Every value entering the model
   is masked, so all downstream math is masked math.

2. **Masked constructors inside the math**: `scalar()` wraps scalars/ndarrays as masked
   arrays, and `cover()` builds a masked array (`np.ma.getdata`/`filled`/re-wrap). These are
   called repeatedly inside `angot_radiation`/`net_absorbed_radiation`.

3. **Python-level `numpy.ma` operator wrappers and mask propagation**: every `+ - * / **`,
   `maximum`, and `np.where` on a masked array dispatches through the `numpy.ma` layer, which
   recomputes and propagates the mask and makes defensive copies, instead of running compiled
   ndarray ufuncs. This is the 1.6x-8.4x per-op penalty measured in the micro-benchmark.

4. **Redundant defensive copies in the trig/sqrt helpers**: `asin`/`acos`/`sqrt` call
   `x.copy()` before clipping out-of-domain values to NaN. On masked inputs this is a masked
   copy; even on plain arrays the copy is only needed when the input must not be mutated.

The secondary I/O costs are independently confirmed: `writenet` reopens/closes the output
file per timestep (~0.46 s x 33 = ~15 s), `create_new_netcdf` uses `zlib=True, complevel=4`,
and `netcdf_step` re-reads the full `time` variable per call (~18 s x 55).

## Correctness Properties

Property 1: Bug Condition - Hot path computes on plain float64 with NaN

_For any_ input where the bug condition holds (a per-timestep grid that today flows through
the math as a `numpy.ma` masked array), the fixed code SHALL perform the computation on a
plain `float64` array using NaN for missing cells, producing a result that is numerically
equivalent to the current masked-array result (equal finite values within the reference
tolerance, NaN in exactly the cells that were masked) while no longer dispatching through the
`numpy.ma` layer.

**Validates: Requirements 2.1, 2.2, 2.6**

Property 2: Preservation - Non-hot-path and boundary behavior is unchanged

_For any_ input where the bug condition does NOT hold (file structure/metadata, the location
and count of missing cells, the `ignore_nan_validation` setting, calendar/split-I/O/unit-
conversion/6-hourly/Hargreaves selection, and the numpy/no-pcraster constraint), the fixed
code SHALL produce the same result as the original implementation, preserving numerically
equivalent output against `tests/data/reference`, DEM NaN-consistency, and identical output
netCDF structure, metadata, scaling, and fill values.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**

## Fix Implementation

Assuming the root-cause analysis is correct, the fix changes the grid representation at the
boundaries and inside the operator layer, keeping formulas untouched. The work is sequenced
Phase A first (highest impact, correctness-critical), then Phase B (independent I/O wins).

### Phase A - De-mask the hot path (primary)

**A1. Read boundary -> plain float64 with NaN**

**File**: `src/lisvap/utils/readers.py`
**Functions**: `readnetcdf`, `loadmap`

1. Stop returning `np.ma.masked_array`. Keep the existing mask application
   (`mapnp[np.isnan(mapnp)] = np.nan; mapnp[maskmap.mask] = np.nan`) and the
   `flatten().reshape(maskmap.shape)`, but return the plain `float64` ndarray (NaN already in
   masked cells). This is the single point where the mask is applied on read (Requirement
   2.2).
2. Ensure the returned dtype is `float64` so downstream arithmetic matches current precision
   (the masked arrays were float64). Cast explicitly if the source variable is integer.
3. Keep unit conversion (`mapnp = mapnp * conversion_factor`) and the
   `negative_value_substitute` handling exactly as they are - they already operate on the
   plain `mapnp` before wrapping.

**A2. Operator layer -> plain float64 with NaN**

**File**: `src/lisvap/utils/operators.py`

1. `scalar()`: return a plain `float64` array. For a scalar input, `np.full(maskmap.shape,
   value, dtype=float64)` then set `result[maskmap.mask] = np.nan`. For an ndarray input,
   `flatten().reshape(maskmap.shape)` then apply NaN at `maskmap.mask`. Drop the
   `np.ma.MaskedArray` branch (inputs will no longer be masked), or make it accept an ndarray
   and copy.
2. `cover()`: operate on a plain array - `arr = scalar(input_map)` (now plain), then
   `arr[np.isnan(arr)] = mv`. Note this fills ALL NaN including masked cells, matching the
   current `filled()`-based behavior; re-masking happens at the write boundary and is
   re-asserted by cover's callers that follow with `maximum`/`ifthenelse` as today.
3. `sqr`, `exp`, `maximum`, `ifthenelse` (`np.where`), `abs`: no change - these are already
   plain numpy ufuncs that operate correctly on `float64`-with-NaN and propagate NaN.
4. `asin`, `acos`, `sqrt`: keep the pcraster-compatible behavior (out-of-domain -> NaN,
   positive angles via `+= 2*pi` on negative radians, `round_decimals`). Avoid the
   unnecessary `.copy()` where the input is a fresh intermediate that may be mutated in place;
   where a defensive copy is still required (the input array is reused by the caller), keep a
   plain `np.array(x, copy=True)` rather than a masked copy. Behavior (NaN placement, angle
   values) must be identical.
5. `round_decimals`, `sin`, `cos`, `tan`: unchanged; they already call `np.round`/`np.deg2rad`
   which work on plain arrays.
6. `defined()`: unchanged; already uses `np.isnan` on a plain array.

**A3. Hot path consumers**

**Files**: `src/lisvap/lisvapdynamic.py`, `src/lisvap/hydrological/readmeteo.py`

- No formula changes. These modules consume `self.TAvg/TMin/TMax/EAct/ESat/Wind/Dem/Lat/...`
  (now plain `float64`-with-NaN from A1) and call the operators from A2. Verify that every
  constant combined with a grid stays `float64` (Python floats upcast fine) and that
  `ifthenelse`/`maximum` branches still route NaN correctly (NaN compares False, so
  `np.where(cond, a, b)` keeps NaN from whichever branch supplies it - identical to the
  masked behavior where masked cells stayed masked).
- `self.ETRef/ESRef/EWRef` become plain `float64`-with-NaN arrays. No change needed here
  beyond what A1/A2 provide.

**A4. Write boundary + NaN-consistency**

**Files**: `src/lisvap/utils/writers.py`, `src/lisvap/utils/output.py`

1. `writenet`: replace `inputmap.filled(np.nan)[slices]` with handling for a plain array.
   Since the array already carries NaN in masked cells, use
   `mapnp = np.asarray(inputmap, dtype=float64)[slices]` (no `.filled`). The subsequent
   `mapnp[np.isnan(mapnp)] = (nan_value - add_offset) * scale_factor` packing and the
   `set_auto_maskandscale(True)` int16 write are unchanged, so the output file keeps identical
   structure, scaling, and fill values (Requirement 3.6). If `inputmap` could still be a
   masked array during the transition, accept both via `np.ma.filled(inputmap, np.nan)` which
   is a no-op on plain arrays.
2. `output.py` `initial()` and `_check_nan_consistency`: `self.var.Dem` and the output grids
   are now plain arrays. Replace `.filled(np.nan)` with `np.asarray(..., dtype=float64)` (or
   `np.ma.filled(x, np.nan)` to tolerate both representations). The NaN-count comparison logic
   is unchanged, so the DEM NaN-consistency guarantee (Requirement 3.3) still holds.
3. Preserve the `ignore_nan_validation` short-circuit exactly (Requirement 3.4).

### Phase B - Per-timestep I/O optimizations (secondary, independent)

These are separable from Phase A and must not change output file structure, metadata,
scaling, or fill values (Requirement 3.6).

**B1. Keep the output handle open across timesteps** (`utils/writers.py`)
- Avoid `Dataset(netfile, 'a')` + `nf1.close()` on every call. Cache the open `Dataset`
  handle (keyed by resolved `netfile` path) and reuse it across timesteps; flush/close at end
  of run (or when the split-I/O filename changes). Must still create the file on first write
  and respect split/monthly/yearly filename switching in `get_output_parameters`.

**B2. Reduce/remove compression** (`utils/writers.py` `create_new_netcdf`)
- Lower or disable `zlib` compression on the output variable (e.g. `zlib=False` or a lower
  `complevel`). Keep `data_type`, `fill_value`, `scale_factor`, `add_offset`, `valid_min/max`,
  and `set_auto_maskandscale(True)` identical so files remain valid, readable, and
  structurally unchanged.

**B3. Cache the input time axis per open file** (`utils/readers.py` `netcdf_step`)
- Avoid `nf1.variables['time'][:]` on every call. Cache `t_steps` (and the derived
  unit/calendar) keyed by the open `Dataset` so repeated reads of the same file reuse the
  already-read axis. Must invalidate/re-read when the file handle changes (split I/O advancing
  to the next file).

## Testing Strategy

### Validation Approach

Two phases. First, confirm the representation change does not alter numerics by running the
existing reference-comparison suite (the authoritative equivalence oracle). Second, re-profile
the EFAS 1arcmin case to confirm the masked-array machinery no longer dominates and the run is
measurably faster. Because the installed env is a static copy in `site-packages`, all changes
are exercised via `PYTHONPATH=src` (never the installed copy).

### Exploratory Bug Condition Checking

**Goal**: Surface, before changing anything, exactly where masked arrays are created and how
much time they cost, to confirm the root cause and establish the before baseline.

**Test Plan**: Run the EFAS 1arcmin case under cProfile on the current (unfixed) code and
inspect the top cumulative entries; confirm `numpy.ma` functions and `writenet`/`netcdf_step`
dominate. Add a temporary assertion/log at the read boundary and in the hot path confirming
the arrays are `np.ma.MaskedArray` today.

Command (baseline):
```
cd /home/gomesgl@delta.europa.eu/projects/lisflood-lisvap
PYTHONPATH=src python -m cProfile -o before.prof bin/lisvap tests/data/tests_efas_1arcmin.xml
```

**Test Cases**:
1. **Masked-at-read**: assert `readnetcdf(...)` returns a `numpy.ma.MaskedArray` on unfixed
   code (will hold today; will flip to plain ndarray after the fix).
2. **Masked-in-math**: assert `self.ETRef` is a masked array on unfixed code.
3. **Profile dominance**: confirm `numpy.ma`-related cumulative time is ~55-70 s of ~106 s.
4. **I/O overhead (edge/secondary)**: confirm ~15 s in reopen/close and ~18 s in the
   time-axis re-read.

**Expected Counterexamples**:
- Hot-path grids are `numpy.ma` masked arrays and `numpy.ma` dominates the profile.
- Possible contributors: masked read boundary, `scalar`/`cover` constructors, per-op
  `numpy.ma` wrappers and defensive copies.

### Fix Checking

**Goal**: Verify that for all buggy inputs (grids that were masked in the hot path), the fixed
code computes on plain `float64`-with-NaN and produces numerically equivalent output.

**Pseudocode:**
```
FOR ALL grid WHERE isBugCondition(grid) DO
  result := fixedComputation(grid)   # plain float64 with NaN
  ASSERT isPlainFloat64(result)
  ASSERT missingCellsAreNaN(result)
  ASSERT numericallyEquivalentToOriginal(result, tolerance=reference_atol)
END FOR
```

**Test Plan**: Run the full EFAS reference-comparison suite (`tests/tests_efas.py` and the
sibling domain modules) against the committed reference outputs under `tests/data/reference`.
The suite's `check_var_step` already compares every timestep with `atol=0.01` and the
percentage-wrong gates, which is the equivalence oracle for e0/es/et. Add a lightweight unit
assertion that `readnetcdf`/`scalar`/`cover`/`ETRef` now return plain `float64` ndarrays.

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function
produces the same result as the original - identical missing-cell placement, identical output
file structure/metadata/scaling/fill values, and unchanged non-hot-path behavior.

**Pseudocode:**
```
FOR ALL input WHERE NOT isBugCondition(input) DO
  ASSERT originalBehavior(input) = fixedBehavior(input)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation because it
generates many grids across the input domain (including all-missing rows, out-of-domain
trig/sqrt inputs, and mixed finite/NaN patterns) and catches edge cases manual tests miss. The
key invariant: for a plain `float64`-with-NaN grid `g` and its masked equivalent
`np.ma.masked_invalid(g)`, each refactored operator (`scalar`, `cover`, `asin`, `acos`,
`sqrt`, `maximum`, `ifthenelse`) yields values equal (within tolerance) to the original masked
operator on the finite cells and NaN on the missing cells.

**Test Plan**: Observe current behavior on the unfixed masked implementation for each operator
and for the output file metadata, then write property-based and golden tests that assert the
fixed implementation reproduces it.

**Test Cases**:
1. **Operator equivalence**: for random grids, each refactored operator matches the original
   masked operator on finite cells and preserves NaN on missing cells.
2. **DEM NaN-consistency**: output NaN count equals the DEM-derived count for every timestep
   (the `_check_nan_consistency` guard stays green).
3. **File metadata golden**: compare output netCDF structure, variables, dims, `scale_factor`,
   `add_offset`, `valid_min/max`, `missing_value`/`_FillValue`, and packed dtype before vs
   after (must be byte-compatible for structure/metadata).
4. **Non-hot-path matrix**: run the cordex, glofas, hargreaves, rel-humidity-360-cal,
   6-hourly, yearly, hourly, and 360-day-calendar suites to cover unit conversion, calendar
   handling, split I/O, 6-hourly replication, and Hargreaves-vs-Penman selection.
5. **ignore_nan_validation**: with the setting on, the NaN check is skipped; with it off, the
   check runs - behavior identical before/after.

### Unit Tests

- `scalar`/`cover` return plain `float64`-with-NaN with the correct values and NaN placement.
- `asin`/`acos`/`sqrt` map out-of-domain inputs to NaN and keep positive-angle/rounding
  behavior, without masked copies.
- `readnetcdf`/`loadmap` return plain `float64` ndarrays with NaN in masked cells and correct
  unit conversion / negative-value substitution.
- `writenet` packs a plain `float64`-with-NaN array into the int16 output identically to the
  previous masked-array path.

### Property-Based Tests

- Generate random `float64` grids with random NaN masks; assert operator-by-operator
  equivalence between the fixed plain-array path and the original masked path on finite cells,
  and NaN preservation on missing cells.
- Generate random valid/invalid trig and sqrt inputs; assert out-of-domain -> NaN and
  in-domain equality with the original.
- Generate random grids and assert the write->read round trip reproduces values within the
  packing tolerance and preserves the NaN pattern.

### Integration Tests

- Full EFAS 1arcmin run reproduces `tests/data/reference/efas_1arcmin` for e0/es/et across all
  timesteps (equivalence).
- Full runs for every other domain suite pass (regression across calendars, split I/O,
  6-hourly, yearly, Hargreaves, cordex, glofas).
- **Performance re-profile (after)**: rerun under cProfile and compare to `before.prof`;
  confirm `numpy.ma` is no longer dominating and total wall-clock is measurably lower on the
  EFAS 1arcmin case.
  ```
  PYTHONPATH=src python -m cProfile -o after.prof bin/lisvap tests/data/tests_efas_1arcmin.xml
  ```
- After Phase B, confirm the reopen/close and time-axis-re-read costs are reduced and output
  files remain structurally identical to Phase A output.
