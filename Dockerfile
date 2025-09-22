FROM continuumio/miniconda3

LABEL maintainer="Goncalo Gomes <goncalo.ramos-gomes@ext.ec.europa.eu>"

ENV DEBIAN_FRONTEND=noninteractive

# Install requirements
RUN apt-get update && \
    apt-get -y install gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Create conda "lisvap" environment:
COPY environment.yml /
RUN conda update -n base -c defaults conda
# RUN conda create -n lisvap -f /environment.yml
RUN conda create -n lisvap -c conda-forge -y python=3.8 gdal numpy pcraster

COPY requirements.txt /
RUN conda run -n lisvap pip install -r /requirements.txt --ignore-installed

WORKDIR /
COPY basemaps/. /basemaps/
COPY src/. /
COPY LICENSE /
COPY settings_tpl.xml /

# RUN Tests
COPY tests/. /tests/
COPY pytest.ini /tests
# RUN conda run -n lisvap python -m pytest /tests -x -l -ra

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
