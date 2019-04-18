#!/usr/bin/env bash

set -e
if [[ "$1" = 'test' ]]; then
    echo "RUNNING tests....."
    pytest /lisvap/tests/ -s
    mkdir -p /output/cordex
    mkdir -p /output/efas
    echo "copy produced files to /output/cordex......"
    cp /lisvap/tests/data/output/cordex/*.nc /output/cordex/
    cp /lisvap/tests/data/tests_cordex.xml /output/cordex/
    echo "copy produced files to /output/efas......"
    cp /lisvap/tests/data/output/efas/*.nc /output/efas/
    cp /lisvap/tests/data/tests_efas.xml /output/efas/
else
    exec python /lisvap/lisvap1.py "$@"
fi
