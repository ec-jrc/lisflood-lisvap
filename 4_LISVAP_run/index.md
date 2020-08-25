## Running LISVAP

There is no difference between running LISVAP in a Docker container, as an installed python module, or using the source code. In each case, you'll need to prepare your XML settings file and pass it to LISVAP as an argument.

You can find the description of the settings file together with the link to the template in [LISVAP Settings file](/lisflood-lisvap/3_2_LISVAP_settingsfile/).

This page provides the instructions to run LISVAP, presuming that you have prepared your own base maps, the meteorological input and settings files. 
In order to help you to get started we have prepared [two case studies](https://ec-jrc.github.io/lisflood-lisvap/6_LISVAP_tests/) that you can try out after reading this page.


### ... in a Docker container

In order to run LISVAP using a Docker container, you need to map the folders using volumes as in the table below. Those paths are configured in the XML settings file that you submit to LISVAP.


   **Table:** *Mapping volumes to run LISVAP in Docker*
   

| Volume                            |  Example of folder on your system |  Correspondant folder in Docker | Mapping                        |
| --------------------------------- | --------------------------------- | ------------------------------- | ------------------------------ |
| Folder with the XML settings file | ./                                | /tmp                            | -v $(pwd)/:/tmp                |
| Path containing input dataset     | /DATA/Meteo/EMA                   | /input                          | -v /DATA/Meteo/EMA:/input      |
| Path for output                   | /DATA/Lisvap/out                  | /output                         | -v /DATA/Lisvap/out:/output    |

Then, the corresponding Docker command (in Linux) to run the LISVAP container, given mysettings.xml is in current folder, will be:

```bash
docker pull efas/lisvap:latest
docker run -v $(pwd)/:/tmp -v /DATA/Meteo/EMA:/input -v /DATA/Lisvap/out:/output efas/lisvap:latest /tmp/mysettings.xml -v -t
```

Note that in the above command we added two options (arguments) at the end. You can find the whole list of available options in the usage dialogue below.
You can print the usage dialogue by typing `docker run efas/lisvap:latest`, which is the equivalent to calling LISVAP without any arguments.

 ```console
LisvapPy - Lisvap (Global) using pcraster Python framework

    Version      : 0.3.4
    Last updated : 23/05/2019
    Status       : Development
    Authors      : Peter Burek, Johan van der Knijff, Ad de Roo
    Maintainers  : Domenico Nappo, Valerio Lorini, Lorenzo Mentaschi

    Arguments list:

    settings.xml     settings file

    -q --quiet       output progression given as .
    -v --veryquiet   no output progression is given
    -l --loud        output progression given as time step, date and discharge
    -c --checkfiles  input maps and stack maps are checked, output for each input map BUT no model run
    -h --noheader    .tss file have no header and start immediately with the time series
    -t --printtime   the computation time for hydrological modules are printed

 ```

### ... as an installed python module

If you installed LISVAP in your python environment using pip tool, you will have a binary called `lisvap` in your path.

```bash
pip install lisflood-lisvap
lisvap mysettings.xml -v -t
```

### ... from source code

Once all dependencies are installed, you can run the model using python interpreter. As previously said, we strongly recommend using an isolated python virtualenv.

```bash
python src/lisvap1.py mysettings.xml -v -t
```
