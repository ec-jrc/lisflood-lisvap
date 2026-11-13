# Implementation Plan

All changes are exercised via `PYTHONPATH=src` because the installed env is a static copy in
`site-packages`. Keep every change incremental so the reference-comparison suite can be run
between steps. The reference suites live under `tests/` (`tests_efas.py`, `tests_cordex.py`,
`tests_glofas.py`, `tests_hargreaves.py`, `tests_relative_humidity.py`) and compare against
`tests/data/reference` with `atol=0.01` and the per-step percentage-wrong gates in
`tests/__init__.py`.

- [x] 1. Write bug condition exploration test + establish before baseline
  - **Property 1: Bug Condition** - Hot path computes on numpy.ma masked arrays
  - **CRITICAL**: This test MUST FAIL on fixed code and PASS on current (unfixed) code - it
    asserts the *present* defect (masked arrays in the hot path). It flips to failing once the
    fix lands, which is the signal the representation changed. Keep it as the record of the
    bug condition; the equivalence oracle (task 3.2) is what proves correctness after the fix.
  - **DO NOT attempt to fix the test or the code when its assertions change**
  - **GOAL**: Surface counterexamples that demonstrate masked arrays dominate the hot path
  - **Scoped PBT Approach**: For this deterministic defect, scope the property to the concrete
    EFAS 1arcmin case and the concrete read/math boundary grids.
  - Add a focused test (e.g. `tests/test_masked_array_perf.py`) asserting, on the current code:
    - `readnetcdf(...)` returns a `numpy.ma.MaskedArray` (Bug Condition: masked-at-read)
    - `scalar(24.)` and `cover(...)` return `numpy.ma.MaskedArray` (masked constructors)
    - `self.ETRef` (or an equivalent hot-path grid) is a `numpy.ma.MaskedArray` (masked-in-math)
  - Establish the profiling baseline and save it:
    `PYTHONPATH=src python -m cProfile -o before.prof bin/lisvap tests/data/tests_efas_1arcmin.xml`
  - Inspect `before.prof` top cumulative entries; document that `numpy.ma` functions account
    for ~55-70 s of ~106 s and that `writenet` reopen/close (~15 s) and `netcdf_step` time-axis
    re-read (~18 s) are present (secondary/edge counterexamples)
  - Confirm the full reference suite passes on the unchanged code (green starting point):
    `PYTHONPATH=src python -m pytest tests/`
  - **EXPECTED OUTCOME**: bug-condition assertions PASS on unfixed code (masked arrays present),
    reference suite is green, `before.prof` saved
  - Document counterexamples (e.g. "readnetcdf('tair', t) is a MaskedArray; np.ma.* dominates
    the cumulative profile") to anchor the root cause
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  - _Bug_Condition: isBugCondition(input) = isMaskedArray(input) AND flowsThroughPerTimestepMath(input)_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Operator equivalence, NaN-consistency, and file metadata
  - **IMPORTANT**: Follow observation-first methodology - observe current masked behavior, then
    write tests that assert the observed behavior across the input domain
  - Observe current (unfixed) operator outputs on random grids, then write property-based tests:
    for a plain `float64`-with-NaN grid `g` and its masked equivalent `np.ma.masked_invalid(g)`,
    each operator (`scalar`, `cover`, `asin`, `acos`, `sqrt`, `maximum`, `ifthenelse`) must yield
    equal values (within tolerance) on finite cells and NaN on missing cells
  - Add property-based tests (Hypothesis) for out-of-domain `asin`/`acos`/`sqrt` -> NaN and
    in-domain equality with the original masked operator
  - Capture the output file metadata golden on unfixed code: structure, variables, dims,
    `scale_factor`, `add_offset`, `valid_min/max`, `missing_value`/`_FillValue`, packed dtype
  - Record the DEM NaN-consistency baseline (`_check_nan_consistency`) and the
    `ignore_nan_validation` on/off behavior
  - Run these on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (confirms the baseline behavior to preserve)
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6, 3.7_

- [x] 3. Phase A - De-mask the hot path (primary, correctness-critical)

  - [x] 3.1 Convert the read boundary to plain float64-with-NaN
    - `src/lisvap/utils/readers.py` `readnetcdf`, `loadmap`: stop returning
      `np.ma.masked_array`; keep mask application (`mapnp[np.isnan(mapnp)] = np.nan;
      mapnp[maskmap.mask] = np.nan`) and `flatten().reshape(maskmap.shape)`, return the plain
      `float64` ndarray
    - Ensure returned dtype is `float64` (cast explicitly if the source variable is integer)
    - Keep unit conversion (`mapnp * conversion_factor`) and `negative_value_substitute`
      handling exactly as today (they operate on plain `mapnp` before wrapping)
    - Run the reference suite to prove equivalence after this boundary change:
      `PYTHONPATH=src python -m pytest tests/`
    - _Bug_Condition: isBugCondition(input) - masked-at-read boundary_
    - _Expected_Behavior: isPlainFloat64(result) AND missingCellsAreNaN(result) AND numericallyEquivalentToOriginal(result, atol=0.01)_
    - _Preservation: unit conversion, negative-value substitution, NaN placement unchanged_
    - _Requirements: 2.1, 2.2, 3.1, 3.3_

  - [x] 3.2 Convert the operator layer to plain float64-with-NaN
    - `src/lisvap/utils/operators.py`:
      - `scalar()`: return plain `float64`. Scalar input -> `np.full(maskmap.shape, value,
        dtype=float64)` then `result[maskmap.mask] = np.nan`. ndarray input ->
        `flatten().reshape(maskmap.shape)` then NaN at `maskmap.mask`. Drop the masked branch
        (or accept an ndarray and copy)
      - `cover()`: operate on a plain array - `arr = scalar(input_map)` then
        `arr[np.isnan(arr)] = mv` (fills all NaN incl. masked, matching current `filled()`)
      - `asin`, `acos`, `sqrt`: keep pcraster-compat (out-of-domain -> NaN, positive angles via
        `+= 2*pi`, `round_decimals`); remove the unnecessary `.copy()`, keeping a plain
        `np.array(x, copy=True)` only where a defensive copy is genuinely needed
      - `sqr`, `exp`, `maximum`, `ifthenelse`, `abs`, `round_decimals`, `sin`, `cos`, `tan`,
        `defined`: no change (already plain-numpy correct on float64-with-NaN)
    - Run the operator equivalence unit + property-based tests from task 2 and the reference
      suite: `PYTHONPATH=src python -m pytest tests/`
    - _Bug_Condition: isBugCondition(input) - masked constructors / masked operator wrappers / defensive copies_
    - _Expected_Behavior: operators return plain float64, equal finite values, NaN preserved, no numpy.ma dispatch_
    - _Preservation: pcraster-compat behavior (NaN placement, angle values, rounding) unchanged_
    - _Requirements: 2.1, 2.2, 3.1, 3.5_

  - [x] 3.3 Convert the write boundary and NaN-consistency to plain arrays
    - `src/lisvap/utils/writers.py` `writenet`: replace `inputmap.filled(np.nan)[slices]` with
      `np.ma.filled(inputmap, np.nan)` (no-op on plain arrays, tolerates masked during
      transition) then `[slices]`; keep the `mapnp[np.isnan(mapnp)] = (nan_value - add_offset)
      * scale_factor` packing and `set_auto_maskandscale(True)` int16 write unchanged so file
      structure/scaling/fill values are identical
    - `src/lisvap/utils/output.py` `initial()` and `_check_nan_consistency`: replace
      `.filled(np.nan)` with `np.ma.filled(x, np.nan)` (tolerates both representations); keep
      the NaN-count comparison logic and the `ignore_nan_validation` short-circuit exactly
    - Run the DEM NaN-consistency + file-metadata golden tests from task 2 and the reference
      suite: `PYTHONPATH=src python -m pytest tests/`
    - _Bug_Condition: isBugCondition(input) - masked array expected at write boundary_
    - _Expected_Behavior: plain float64-with-NaN packs identically to the previous masked path_
    - _Preservation: output structure/metadata/scaling/fill values, DEM NaN-consistency, ignore_nan_validation unchanged_
    - _Requirements: 2.2, 3.3, 3.4, 3.6_

  - [x] 3.4 Verify hot-path consumers need no formula changes
    - `src/lisvap/lisvapdynamic.py`, `src/lisvap/hydrological/readmeteo.py`: confirm the
      per-timestep math (`evapotranspiration_using_penman_monteith`, `angot_radiation`,
      `net_absorbed_radiation`, `int_solar_height_*`, `evapotranspiration_using_hargreaves`,
      `latent_heat_vaporization`, `ESat`/`EAct`/`Wind`) works unchanged on plain
      `float64`-with-NaN; verify constants upcast to `float64` and `ifthenelse`/`maximum`
      route NaN as before
    - Confirm `self.ETRef/ESRef/EWRef` are plain `float64`-with-NaN arrays with no code change
      needed beyond 3.1-3.3
    - Run the full reference suite: `PYTHONPATH=src python -m pytest tests/`
    - _Bug_Condition: isBugCondition(input) - hot-path grids flowing as masked arrays_
    - _Expected_Behavior: formulas unchanged, results numerically equivalent on plain arrays_
    - _Preservation: numerical formulas in lisvapdynamic.py and readmeteo.py unchanged_
    - _Requirements: 2.1, 3.1, 3.5, 3.7_

  - [x] 3.5 Verify bug condition exploration test reflects the fix
    - **Property 1: Expected Behavior** - Hot path computes on plain float64 with NaN
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The task 1 assertions encoded the bug condition (masked arrays); update them to their
      post-fix counterparts (`readnetcdf`/`scalar`/`cover`/`ETRef` now return plain `float64`
      ndarrays with NaN in masked cells), which confirms the expected behavior is satisfied
    - Add the lightweight unit assertion from the design: `readnetcdf`/`scalar`/`cover`/`ETRef`
      return plain `float64` ndarrays
    - **EXPECTED OUTCOME**: hot-path grids are plain `float64`-with-NaN (bug condition no longer holds)
    - _Requirements: 2.1, 2.2 (Expected Behavior Properties from design Property 1)_

  - [x] 3.6 Verify preservation tests still pass after Phase A
    - **Property 2: Preservation** - Operator equivalence, NaN-consistency, and file metadata
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run operator equivalence, DEM NaN-consistency, file-metadata golden, and
      `ignore_nan_validation` tests plus the reference-comparison suite (equivalence oracle,
      `atol=0.01`): `PYTHONPATH=src python -m pytest tests/`
    - **EXPECTED OUTCOME**: Tests PASS (no regressions; output numerically equivalent)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6_

- [x] 4. Phase B - Per-timestep I/O optimizations (secondary, independent)

  Each Phase B change MUST NOT alter output file structure, metadata, scaling, or fill values.
  Run the reference suite after each sub-task to confirm no regression.

  - [x] 4.1 Keep the output netCDF handle open across timesteps
    - `src/lisvap/utils/writers.py`: avoid `Dataset(netfile, 'a')` + `nf1.close()` per call;
      cache the open `Dataset` keyed by resolved `netfile` path and reuse across timesteps
    - Respect split/monthly/yearly filename switching in `get_output_parameters` (close/reopen
      when the filename changes); flush/close all handles at end of run
    - Still create the file on first write
    - Run the reference suite incl. split/monthly/yearly cases:
      `PYTHONPATH=src python -m pytest tests/`
    - _Bug_Condition: n/a (independent I/O optimization)_
    - _Expected_Behavior: reopen/close per timestep eliminated; output files structurally identical_
    - _Preservation: output structure/metadata/scaling/fill values, split I/O behavior unchanged_
    - _Requirements: 2.3, 3.6, 3.7_

  - [x] 4.2 Reduce/remove compression in create_new_netcdf
    - `src/lisvap/utils/writers.py` `create_new_netcdf`: lower or disable `zlib` compression
      (`zlib=False` or lower `complevel`)
    - Keep `data_type`, `fill_value`, `scale_factor`, `add_offset`, `valid_min/max`, and
      `set_auto_maskandscale(True)` identical so files remain valid, readable, structurally
      unchanged
    - Re-run the file-metadata golden test from task 2 and the reference suite:
      `PYTHONPATH=src python -m pytest tests/`
    - _Bug_Condition: n/a (independent I/O optimization)_
    - _Expected_Behavior: per-write compression cost reduced; files still valid and readable_
    - _Preservation: output dtype/fill/scaling/metadata and readability unchanged_
    - _Requirements: 2.4, 3.6_

  - [x] 4.3 Cache the input time axis per open file in netcdf_step
    - `src/lisvap/utils/readers.py` `netcdf_step`: avoid `nf1.variables['time'][:]` per call;
      cache `t_steps` (and derived unit/calendar) keyed by the open `Dataset`
    - Invalidate/re-read when the file handle changes (split I/O advancing to the next file)
    - Run the reference suite incl. split-input and calendar cases (360_day, no_leap):
      `PYTHONPATH=src python -m pytest tests/`
    - _Bug_Condition: n/a (independent I/O optimization)_
    - _Expected_Behavior: full time-axis re-read eliminated; correct timestep still selected_
    - _Preservation: timestep selection, calendar/split-I/O handling unchanged_
    - _Requirements: 2.5, 3.7_

- [x] 5. Final - Re-profile and run the full domain test matrix
  - Re-profile the EFAS 1arcmin case and save `after.prof`:
    `PYTHONPATH=src python -m cProfile -o after.prof bin/lisvap tests/data/tests_efas_1arcmin.xml`
  - Compare `after.prof` to `before.prof`; confirm `numpy.ma` no longer dominates the
    cumulative profile and wall-clock is measurably lower; confirm the reopen/close and
    time-axis-re-read costs from Phase B are reduced
  - Run the full domain test matrix to confirm no regressions (efas; efas_1arcmin variants
    incl. 6hourly/hourly/yearly/360-day; cordex; glofas; hargreaves; rel_humidity_360_cal):
    `PYTHONPATH=src python -m pytest tests/`
  - Confirm Phase B output files remain structurally identical to Phase A output
  - _Requirements: 2.6, 3.1, 3.2, 3.6, 3.7_

- [x] 6. Checkpoint - Ensure all tests pass
  - Ensure the full reference suite, the operator unit/property-based tests, and the
    performance re-profile all confirm equivalence and a measurable speedup
  - Ensure all tests pass, ask the user if questions arise
