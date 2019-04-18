#!/usr/bin/env bash

docker build -t efas/lisvap:latest .
docker tag efas/lisvap:latest index.docker.io/efas/lisvap:latest
