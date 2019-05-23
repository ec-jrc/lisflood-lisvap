FROM python:3.6-stretch
MAINTAINER Domenico Nappo <domenico.nappo@gmail.com>

ENV no_proxy=jrc.it,localhost,ies.jrc.it,127.0.0.1,jrc.ec.europa.eu
ENV ftp_proxy=http://10.168.209.72:8012
ENV https_proxy=http://10.168.209.72:8012
ENV http_proxy=http://10.168.209.72:8012
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH=/opt/cmake-3.14.1-Linux-x86_64/bin:/opt/pcraster/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${PATH}
ENV PYTHONPATH=/opt/pcraster/python:${PYTHONPATH}
ENV TZ=Europe/RomeB

RUN echo 'Acquire::https::Proxy "http://10.168.209.72:8012";' >> /etc/apt/apt.conf.d/30proxy \
    && echo 'Acquire::http::Proxy "http://10.168.209.72:8012";' >> /etc/apt/apt.conf.d/30proxy
RUN apt-get update && apt-get install -y --no-install-recommends software-properties-common apt-file apt-utils
RUN apt-file update

#RUN apt install -y --no-install-recommends gcc g++ git libboost-all-dev libpython-dev libxerces-c-dev libxml2 libxml2-utils libxslt1-dev qtbase5-dev \
#    libqwt-dev gfortran gdal-bin libgdal-dev python-gdal libqt5opengl5 libqt5opengl5-dev \
#    && pip install docopt numpy==1.15 pytest
RUN apt install -y --no-install-recommends gcc g++ git qtbase5-dev libncurses5-dev libqwt-qt5-dev libxerces-c-dev libboost-all-dev libgdal-dev python3-numpy python3-docopt

RUN cd /opt
RUN wget -q https://cmake.org/files/LatestRelease/cmake-3.14.1-Linux-x86_64.tar.gz && tar -xzvf cmake-3.14.1-Linux-x86_64.tar.gz
RUN wget -q http://pcraster.geo.uu.nl/pcraster/4.2.1/pcraster-4.2.1.tar.bz2 && tar xf pcraster-4.2.1.tar.bz2
RUN mkdir /lisvap && mkdir /input && mkdir /output
RUN mkdir /tests && mkdir /basemaps
RUN cd pcraster-4.2.1 && mkdir build && cd build
RUN cmake -DFERN_BUILD_ALGORITHM:BOOL=TRUE -DCMAKE_INSTALL_PREFIX:PATH=/opt/pcraster -DPYTHON_EXECUTABLE:FILEPATH=/usr/bin/python3 .. \
   && cmake --build . && make install

WORKDIR /
COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY tests/. /tests/
COPY basemaps/. /basemaps/
COPY src/. /
COPY LICENSE /
COPY settings_tpl.xml /
COPY docker-entrypoint.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]
