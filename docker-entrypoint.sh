#!/usr/bin/env bash

set -e
if [[ "$1" = 'usecases' ]]; then
    mkdir -p /input/basemaps
    mkdir -p /input/cordex
    mkdir -p /input/efas
    mkdir -p /input/efas_1arcmin
    mkdir -p /input/efas_1arcmin_6hourly
    mkdir -p /input/efas_1arcmin_360days_calendar
    mkdir -p /input/efas_1arcmin_hourly
    mkdir -p /input/efas_1arcmin_yearly
    mkdir -p /input/glofas
    mkdir -p /input/hargreaves
    mkdir -p /input/rel_humidity_360_cal

    echo "Copying basemaps to /input/..."
    cp -r /basemaps/* /input/basemaps/

    echo "copy input files to /input/cordex......"
    cp /tests/data/input/cordex/*.nc /input/cordex/
    echo "copy cordex settings to /input/..."
    cp /tests/data/tests_cordex.xml /input/

    echo "copy input files to /input/efas......"
    cp /tests/data/input/efas/*.nc /input/efas/
    echo "copy efas settings to /input/..."
    cp /tests/data/tests_efas.xml /input/

    echo "copy input files to /input/efas_1arcmin......"
    cp /tests/data/input/efas_1arcmin/*.nc /input/efas_1arcmin/
    echo "copy efas_1arcmin settings to /input/..."
    cp /tests/data/tests_efas_1arcmin.xml /input/
    
    echo "copy input files to /input/efas_1arcmin_6hourly......"
    cp /tests/data/input/efas_1arcmin_6hourly/*.nc /input/efas_1arcmin_6hourly/
    echo "copy efas_1arcmin_6hourly settings to /input/..."
    cp /tests/data/tests_efas_1arcmin_6hourly.xml /input/

    echo "copy input files to /input/efas_1arcmin_360days_calendar......"
    cp /tests/data/input/efas_1arcmin_360days_calendar/*.nc /input/efas_1arcmin_360days_calendar/
    echo "copy efas_1arcmin_360days_calendar settings to /input/..."
    cp /tests/data/tests_efas_1arcmin_360days_calendar.xml /input/

    echo "copy input files to /input/efas_1arcmin_hourly......"
    cp /tests/data/input/efas_1arcmin_hourly/*.nc /input/efas_1arcmin_hourly/
    echo "copy efas_1arcmin_hourly settings to /input/..."
    cp /tests/data/tests_efas_1arcmin_hourly.xml /input/

    echo "copy input files to /input/efas_1arcmin_yearly......"
    cp /tests/data/input/efas_1arcmin_yearly/*.nc /input/efas_1arcmin_yearly/
    echo "copy efas_1arcmin_yearly settings to /input/..."
    cp /tests/data/tests_efas_1arcmin_yearly.xml /input/
    echo "copy efas_1arcmin_yearly_output settings to /input/..."
    cp /tests/data/tests_efas_1arcmin_yearly_output.xml /input/

    echo "copy input files to /input/glofas......"
    cp /tests/data/input/glofas/*.nc /input/glofas/
    echo "copy glofas settings to /input/..."
    cp /tests/data/tests_glofas.xml /input/

    echo "copy input files to /input/hargreaves......"
    cp /tests/data/input/hargreaves/*.nc /input/hargreaves/
    echo "copy hargreaves settings to /input/..."
    cp /tests/data/tests_hargreaves.xml /input/

    echo "copy input files to /input/rel_humidity_360_cal......"
    cp /tests/data/input/rel_humidity_360_cal/*.nc /input/rel_humidity_360_cal/
    echo "copy rel_humidity settings to /input/..."
    cp /tests/data/tests_rel_humidity_360_cal.xml /input/

    chmod a+w /input/*.xml
elif [[ "$1" = 'tests' ]]; then
    # execute unit tests
    exec conda run -n lisvap pytest /tests -x -l -ra
else
    exec conda run -n lisvap python /lisvap1.py "$@"
fi
