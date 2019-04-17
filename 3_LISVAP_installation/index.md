# Installation of LISVAP

## System requirements

LISVAP is an open source software written in Python and released under EUPL 1.2.
You can run LISVAP as a docker container (preferred way) or by grabbing the source code from github repository and install dependencies on your system.  

If you use Docker to run LISVAP, you need to install Docker software from [docker.com download page](https://www.docker.com/get-started).

Instead; if you want to run LISVAP directly from code (and not using its docker image) you need Python 2.7, some scientific python packages and a recent version of PCRaster.

For Python, ensure to install the latest 2.7 [^1] version for your system [from this page](https://www.python.org/downloads/release/python-2716/).
For details on how to install PCRaster the reader is referred to the PCRaster installation guide [for Windows](http://pcraster.geo.uu.nl/quick-start-guide/) 
or [Linux](http://pcraster.geo.uu.nl/getting-started/pcraster-on-linux/).

[^1]: Next versions of LISVAP will be updated to Python 3.

## Install LISVAP

### Using Docker

Once you ensured you have Docker correctly installed and running on your system, you don't need to install anything else. 
Docker will pull the most updated image from our repository and it will run LISVAP in a container, where all dependencies are satisfied.

To pull the most updated Docker image:

`docker pull efas/lisvap:latest`

### Using the code

While LISVAP is a plain python application and there is no need of explicit compilation/installation/setup steps, you need to install some requirements, though.
To run LISVAP, PCRaster framework and its python interface must be correctly installed. Additionally, you have to install numpy, and netCDF4 (both libraries and python interface).

Just follow these steps:

#### 1. Grab the code

```bash
git clone https://github.com/ec-jrc/lisflood-lisvap.git
cd lisflood-lisvap/
```

#### 2. Install dependencies

```bash
pip install -r requirements.txt
```

For PCRaster, follow official guides:

* [Windows](http://pcraster.geo.uu.nl/quick-start-guide/) 
* [Linux](http://pcraster.geo.uu.nl/getting-started/pcraster-on-linux/)
