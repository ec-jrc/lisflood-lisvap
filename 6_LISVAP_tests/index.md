## LISVAP use cases

We have included two test cases for you to try to run LISVAP. One is using the meteorological input data from the EFAS project and the other one using the data from the CORDEX project.
Each test case includes all the data necessary to do a 15 day simulation, meaning the base maps, meteorological input data and also the prefilled settings file. 
Additionally we also provide the corresponding output files for you to verify your own results.

In order to run the test cases follow the following steps:

### Step 1. Grab the data

You can easily get that data from the Docker container or just by cloning the repository.

**From Docker**

For example, to copy those files from Docker image to your host (e.g. in the folder /local/folder/lisvap/input)

```bash
docker run -v /local/folder/lisvap/input:/input efas/lisvap:latest usecases
```

Then you will receive:

```console
Copying basemaps to /input/...
copy input files to /input/cordex......
copy cordex settings to /input/...
copy input files to /input/efas......
copy efas settings to /input/...
```

After executed the command, you will find data under `/local/folder/lisvap/input` directory, in two subfolders `cordex` and `efas`.


**From source code**

If you clone/download LISVAP github repository, you find relevant files under `basemaps` and `tests/data` folder:

1. [input and settings files](https://github.com/ec-jrc/lisflood-lisvap/tree/master/tests/data)
2. [basemaps](https://github.com/ec-jrc/lisflood-lisvap/tree/master/basemaps)


### Step 2. Adjust settings file

You will find the settings files (*test_efas.xml* and *test_cordex.xml*) in your local directory `/local/folder/lisvap/input`. 
The only thing you need to adjust are paths specifications in the `FILE PATHS` section. 
As the paths definition depends on the execution environment (i.e. Docker or local host), we specified the file path specification in the comment section of each variable


```xml
<group>

    <comment>
        **************************************************************
        FILE PATHS
        **************************************************************
    </comment>

    <textvar name="PathOut" value="/output">
        <comment>
            Output path
            for Docker: /output
            from local host: e.g. E:/lisflood_test/Lisvap/output
        </comment>
    </textvar>

    <textvar name="PathBaseMapsIn" value="/input/basemaps">
        <comment>
            Path to input base maps
            for Docker: /input/basemaps
            from local host: e.g. E:/lisflood_test/Lisvap/input/basemaps
        </comment>
    </textvar>

    <textvar name="PathMeteoIn" value="/input/efas">
        <comment>
            Path to input raw meteo maps
            for Docker: /input/efas or /input/cordex
            from local host: e.g. E:/lisflood_test/Lisvap/input/efas or E:/lisflood_test/Lisvap/input/cordex
        </comment>
    </textvar>

</group>
```

### Step 3. Run

**From Docker**

```bash
docker run -v /:/tmp -v /local/folder/lisvap/input:/input -v /local/folder/lisvap/output:/output efas/lisvap:latest /input/test_efas.xml -v -t
```

**From source code**

Assuming you copied the edited settings file in `/local/folder/lisvap/input/` folder:

```bash
cd src
python lisvap1.py /local/folder/lisvap/input/test_efas.xml -v
```

### Step 4. Verify the output

You will find output maps under the folder you set up in `PathOut`. They are netCDF mapstacks and can be viewed with a netCDF reader like `Panoply` or `ncview`.
You can compare your output to the reference files for [EFAS](https://github.com/ec-jrc/lisflood-lisvap/tree/master/tests/data/reference/efas) and [CORDEX](https://github.com/ec-jrc/lisflood-lisvap/tree/master/tests/data/reference/cordex) found on github repository. 
