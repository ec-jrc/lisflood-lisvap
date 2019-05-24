#!/usr/bin/env bash

docker build -t efas/lisvap:latest .
docker tag efas/lisvap:latest index.docker.io/efas/lisvap:latest

echo "Lisvap Docker image was built. To push to efas docker repository, first do 'docker login' and then:"
echo "'docker push efas/lisvap:latest'"
