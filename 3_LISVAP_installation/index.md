# Installation of LISVAP

LISVAP is an open source software written in Python and released under [EUPL 1.2](https://joinup.ec.europa.eu/collection/eupl/eupl-text-11-12). 

There are three possibilites to get LISVAP:

1. Pull the Docker image (preferred way)
2. Install LISVAP python module using pip tool
3. Clone the repository from github

If you want to run LISVAP as python package (option 2) or directly from code (option 3) you need Python, some scientific python packages and a recent version of PCRaster. The use of a recent Python distribution (>=3.5 works) is strongly recommended; albeit LISVAP also works with Python 2.7, the support for this version will cease late in 2020.
In case you need some exemplary data to run it (basemaps, meteo input etc.), we suggest to install using Docker or by cloning the repository to have access to all those assets.


## Option 1. Pull the Docker image

If you use Docker to run LISVAP, you need to install the Docker software from [docker.com download page](https://www.docker.com/get-started). 
Once you ensured you have Docker correctly installed and running on your system, you don't need to install anything else. 

Docker will pull the most updated image from our repository and it will run LISVAP in a container, where all dependencies are satisfied.

To pull the most updated Docker image, follow those steps: 


#### a. Sign in Docker and install it

You need a user ID and password to download the installer. Create a Docker account in case you haven't got one yet. 
Usually, installation is straight forward; just remember to set up proxies in case your organisation is using it, because Docker does not use the one configured for the system.

#### b. open a terminal window

You send commands to Docker via its CLI so you need a terminal.

**For Windows:** Click 'start' and type **cmd** and press Enter to open a MS-DOS prompt
**For Linux:** Just use key combination Ctrl+Alt+T
**For MacOSX:**  Either open your Applications folder, then open Utilities and double-click on Terminal, or press Command - spacebar to launch Spotlight and type "Terminal," then double-click the search result.

#### c. Pull the LISVAP image
Execute the following command in the terminal:

`docker pull jrce1/lisvap:latest`

Now you have the `jrce1/lisvap` docker image ready to run on your computer.

## Option 2. Install LISVAP python module using pip tool

Easiest and quickest way to get LISVAP is to install its python package into your python 2 distribution (using virtualenv is recommended
 and it's suggested in case you don't need the settings XML template, basemaps nor exemplary input datasets. 

LISVAP module is distributed as a [python pip package](https://pypi.org/project/lisflood-lisvap/) and regularly published to pypi repository. 
Pip is the tool to install python packages/libraries into your python environment, and it manages versions and dependencies.  

Ensure you have a recent Python distribution (>=3.5 works) for your system [from this page](https://www.python.org/downloads/release/python-2716/) along with the pip tool (which is usually already installed).
LISVAP works also with Python 2.7 but keep in mind that its support will be dropped late in 2020.

Pip will install LISVAP python dependencies as well but you still need to compile and install PCRaster and its python interface manually.
For details on how to install PCRaster the reader is referred to the PCRaster installation guide [for Windows](http://pcraster.geo.uu.nl/quick-start-guide/) 
or [Linux](http://pcraster.geo.uu.nl/getting-started/pcraster-on-linux/).

To install LISVAP from pypi repository execute the following command:

```bash
pip install lisflood-lisvap
```


## Option 3. Clone the repository from github

Using option 3 requires having Git installed. Go on the [download page](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and follow instructions for your system.
TODO:  *** write something about git on windows ***


Once git is installed, follow these steps:

#### 1. Grab the code


```bash
git clone https://github.com/ec-jrc/lisflood-lisvap.git
cd lisflood-lisvap
```

#### 2. Install dependencies

We warmly recommend using a `virtualenv` to not pollute python distributions of your system and so to avoid side effects.
To create a virtualenv to run LISVAP in an isolated environment, look at [this guide](https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv). 

After activated the LISVAP virtualenv, you may install dependencies:
 
```bash
pip install -r requirements.txt
```

To install PCRaster, follow official guides:

* [Windows](http://pcraster.geo.uu.nl/quick-start-guide/) 
* [Linux](http://pcraster.geo.uu.nl/getting-started/pcraster-on-linux/)
