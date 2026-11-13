# Bugfix Requirements Document

## Introduction

Lisvap runs noticeably slower than it did before the numpy migration. The v1.4.0 release
("Remove pcraster", CHANGELOG 2026-01-23) replaced all pcraster grid math with numpy, but it
represents every grid as a `numpy.ma` masked array and carries those masked arrays through the
entire per-timestep computation. The masked-array machinery (mask propagation, defensive copies,
and Python-level operator wrappers) dominates the runtime, and secondary per-timestep I/O
behavior compounds it.

Profiling the EFAS 1arcmin case (grid 2970x4530 = 13.45M cells, ~45% masked, 11 timesteps, run
in the `lisflood-lisvap` conda env via `PYTHONPATH=src python bin/lisvap tests/data/tests_efas_1arcmin.xml`
under cProfile) measured ~106 s total wall-clock, of which roughly 55-70 s is masked-array
overhead rather than actual arithmetic. A micro-benchmark at the real grid size showed the
model's core operations run 1.6x-8.4x faster on plain float64 arrays using NaN for missing
values (e.g. `a*b + c` is 8.4x faster, `sqrt` is 4.8x faster).

The fix must preserve the numpy-based implementation (no return to pcraster) and must produce
numerically equivalent output compared to the current implementation, as validated against the
repository's reference outputs under `tests/data/reference` and the per-timestep NaN-consistency
check in `utils/output.py`.

Affected code (all under `src/lisvap/`): `utils/operators.py`, `utils/readers.py`,
`utils/writers.py`, `lisvapdynamic.py`, and `utils/output.py`.

## Bug Analysis

### Current Behavior (Defect)

Lisvap spends the majority of each run inside numpy masked-array machinery and redundant
per-timestep I/O, making runs much slower than the equivalent plain-numpy computation. This
occurs in the `lisflood-lisvap` environment on both VDI and HPC hardware.

1.1 WHEN a simulation runs the per-timestep evapotranspiration, radiation, and Hargreaves math THEN the system carries `numpy.ma` masked arrays through every operation, so mask propagation, defensive copies, and Python-level `numpy.ma` operator wrappers consume roughly 55-70 s of the ~106 s EFAS 1arcmin run instead of being spent on arithmetic

1.2 WHEN grids are produced or consumed THEN the system materializes them as `numpy.ma` masked arrays at read time (`readnetcdf`, `loadmap`) and via `scalar()`/`cover()`, propagating masked-array overhead into all downstream math

1.3 WHEN output is written for each timestep THEN the system reopens the output netCDF file in append mode and closes it again on every timestep (~0.46 s per call, ~15 s across 33 calls in the profiled run)

1.4 WHEN output variables are created THEN the system compresses them with `zlib=True, complevel=4`, adding compression cost to every per-timestep write

1.5 WHEN an input map is read via `netcdf_step` THEN the system re-reads the entire `time` variable (`nf1.variables['time'][:]`) on every call (~18 s across 55 calls in the profiled run)

### Expected Behavior (Correct)

2.1 WHEN a simulation runs the per-timestep evapotranspiration, radiation, and Hargreaves math THEN the system SHALL perform the computation on plain `float64` arrays using NaN for missing values, eliminating the `numpy.ma` masked-array overhead from the hot computation path

2.2 WHEN grids are produced or consumed THEN the system SHALL apply the mask once at read time and once at write time, so that the data flowing through the per-timestep math is plain `float64` with NaN for missing cells rather than `numpy.ma` masked arrays

2.3 WHEN output is written across a multi-timestep run THEN the system SHALL avoid reopening and closing the output netCDF file on every timestep (for example by keeping the handle open across timesteps or buffering writes)

2.4 WHEN output variables are created THEN the system SHALL reduce or remove the per-write compression cost (lowering or disabling `zlib` compression) while still producing valid, readable output files

2.5 WHEN input maps are read across a multi-timestep run THEN the system SHALL avoid re-reading the full `time` axis on every call (for example by caching the time axis per open file)

2.6 WHEN the same simulation is run after the fix THEN the system SHALL complete measurably faster than the current implementation on the EFAS 1arcmin case, with the masked-array machinery no longer dominating the profile

### Unchanged Behavior (Regression Prevention)

3.1 WHEN a simulation completes THEN the system SHALL CONTINUE TO produce output that is numerically equivalent to the current implementation, as validated against the reference outputs under `tests/data/reference`

3.2 WHEN the existing test suites are run (`tests/data/tests_*.xml`, `tests_efas.py`, and the other test modules) THEN the system SHALL CONTINUE TO pass them

3.3 WHEN missing/masked cells are present in inputs THEN the system SHALL CONTINUE TO treat them as missing in outputs, so the amount and location of missing values in the output matches the current behavior and the per-timestep NaN-consistency check against the DEM in `utils/output.py` still holds

3.4 WHEN the `ignore_nan_validation` setting is used THEN the system SHALL CONTINUE TO honor it exactly as it does today

3.5 WHEN the implementation is changed THEN the system SHALL CONTINUE TO use the numpy-based implementation and SHALL NOT reintroduce pcraster

3.6 WHEN output netCDF files are produced THEN the system SHALL CONTINUE TO be readable with the same structure, variables, metadata, scaling/offset, and fill values as the current implementation

3.7 WHEN non-hot-path behavior is exercised (settings parsing, calendar/date handling, split I/O, unit conversion, 6-hourly output, Hargreaves vs Penman-Monteith selection) THEN the system SHALL CONTINUE TO behave as it does today
