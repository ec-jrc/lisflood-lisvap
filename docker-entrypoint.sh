#!/usr/bin/env bash

set -e
if [[ "$1" = 'usecases' ]]; then
#    pytest /lisvap/tests/ -s
    mkdir -p /input/cordex
    mkdir -p /input/efas
    mkdir -p /input/basemaps
    echo "Copying basemaps to /input/..."
    cp /basemaps/* /input/basemaps/
    echo "copy input files to /input/cordex......"
    cp /lisvap/tests/data/input/cordex/*.nc /input/cordex/
    cp /lisvap/tests/data/tests_cordex.xml /input/cordex/

    echo "copy input files to /input/efas......"
    cp /lisvap/tests/data/input/efas/*.nc /input/efas/
    cp /lisvap/tests/data/tests_efas.xml /input/efas/
else
    exec python /lisvap/lisvap1.py "$@"
fi
