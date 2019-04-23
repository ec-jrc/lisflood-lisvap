# Installation of LISVAP

LISVAP is an open source software written in Python and released under [EUPL 1.2](https://joinup.ec.europa.eu/collection/eupl/eupl-text-11-12). There are three possibilites to get LISVAP:

1. Pull the Docker image (preferred way)
2. Install LISVAP python module using pip tool
3. Clone the repository from github

In case you need some exemplary data to run it (basemaps, meteo input etc.), we suggest to install using Docker or by cloning the repository to have access to all assets.


## Pull the Docker image
If you use Docker to run LISVAP, you need to install the Docker software from [docker.com download page](https://www.docker.com/get-started). Once you ensured you have Docker correctly installed and running on your system, you don't need to install anything else. 
Docker will pull the most updated image from our repository and it will run LISVAP in a container, where all dependencies are satisfied.

To pull the most updated Docker image, follow those steps: 


#### 1. log in to Docker
You need a user ID and password. Create a Docker account in case you haven't got one yet

#### 2. open a MS-DOS prompt
Click 'start' and type **cmd** and press Enter

#### 3. Make a pull request
Execute the following command:

`docker pull efas/lisvap:latest`


## Install LISVAP python module using pip tool

LISVAP module is distributed as a pip package and regularly published to pypi repository.

To install[^2]

`pip install lisflood-lisvap`


## Clone the repository from github
If you want to run LISVAP directly from code (and not using its docker image) you need Python 2.7, some scientific python packages and a recent version of PCRaster.

For Python, ensure to install the latest 2.7 [^1] version for your system [from this page](https://www.python.org/downloads/release/python-2716/).
For details on how to install PCRaster the reader is referred to the PCRaster installation guide [for Windows](http://pcraster.geo.uu.nl/quick-start-guide/) 
or [Linux](http://pcraster.geo.uu.nl/getting-started/pcraster-on-linux/).

To run LISVAP, PCRaster framework its dependencies (NOT CLEAR!!!), and its python interface must be correctly installed. Additionally, you have to install numpy and netCDF4 (both libraries and python interface).

Just follow these steps:

#### 1. Grab the code

(BUT THIS IS NOW IN LINUX!!, YOU DIDn'T SAY THAT)
```bash
git clone https://github.com/ec-jrc/lisflood-lisvap.git
cd lisflood-lisvap/
```

#### 2. Install dependencies

We warmly recommend using a `virtualenv` to not pollute the python distribution of your system and to avoid side effects.
To create a virtualenv to run LISVAP in an isolated environment, follow [this guide](https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv). 
After activated the LISVAP virtualenv, install dependencies:
 
```bash
pip install -r requirements.txt
```

To install PCRaster, follow official guides:

* [Windows](http://pcraster.geo.uu.nl/quick-start-guide/) 
* [Linux](http://pcraster.geo.uu.nl/getting-started/pcraster-on-linux/)

[^1]: Next versions of LISVAP will be updated to Python 3.
[^2]: Remember that pip installation of lisvap will install its python dependencies as well but you still need to install PCRaster python manually.
