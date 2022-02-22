#!/usr/bin/env bash

docker build -t jrce1/lisvap:latest .
docker tag jrce1/lisvap:latest index.docker.io/jrce1/lisvap:latest
docker tag jrce1/lisvap:latest d-registry.jrc.it:5000/e1-smfr/lisvap:latest

echo
echo
echo "Lisvap Docker image was built. To push to jrce1 docker repository, first do 'docker login' and then:"
echo "'docker push jrce1/lisvap:latest'"
echo
echo
