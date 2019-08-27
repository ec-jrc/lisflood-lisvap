FROM python:3.5-stretch
MAINTAINER Domenico Nappo <domenico.nappo@gmail.com>

ENV no_proxy=jrc.it,localhost,ies.jrc.it,127.0.0.1,jrc.ec.europa.eu
ENV ftp_proxy=http://10.168.209.72:8012
ENV https_proxy=http://10.168.209.72:8012
ENV http_proxy=http://10.168.209.72:8012
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH=/opt/pcraster/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${PATH}
ENV PYTHONPATH=/opt/pcraster/python:${PYTHONPATH}
ENV TZ=Europe/RomeB

RUN echo 'Acquire::https::Proxy "http://10.168.209.72:8012";' >> /etc/apt/apt.conf.d/30proxy \
    && echo 'Acquire::http::Proxy "http://10.168.209.72:8012";' >> /etc/apt/apt.conf.d/30proxy
RUN apt-get update && apt-get install -y --no-install-recommends software-properties-common apt-file apt-utils
RUN apt-file update
RUN apt-get install -y --no-install-recommends gcc g++ git cmake \
                    qtbase5-dev libncurses5-dev libqwt-qt5-dev libqt5opengl5-dev libqt5opengl5 \
                    libxerces-c-dev libboost-all-dev libgdal-dev python3-numpy python3-docopt \
  && mkdir /lisvap && mkdir /input && mkdir /output && mkdir /tests && mkdir /basemaps

WORKDIR /opt
RUN wget -q http://pcraster.geo.uu.nl/pcraster/4.2.1/pcraster-4.2.1.tar.bz2 && tar xf pcraster-4.2.1.tar.bz2 && rm pcraster-4.2.1.tar.bz2 && cd pcraster-4.2.1 && mkdir build

COPY requirements.txt /
RUN pip3 install -U pip && pip3 install -r /requirements.txt \
 && cd /usr/lib/x86_64-linux-gnu/ && ln -s libboost_python-py35.so libboost_python3.so

WORKDIR /opt/pcraster-4.2.1/build
RUN cmake -DFERN_BUILD_ALGORITHM:BOOL=TRUE -DCMAKE_INSTALL_PREFIX:PATH=/opt/pcraster -DPYTHON_EXECUTABLE:FILEPATH=/usr/bin/python3.5 ../ \
   && cmake --build ./ && make install

COPY tests/. /tests/
COPY basemaps/. /basemaps/
COPY src/. /
COPY LICENSE /
COPY settings_tpl.xml /
COPY docker-entrypoint.sh /
RUN pytest /tests/regression_tests.py -s
ENTRYPOINT ["/docker-entrypoint.sh"]
