## LISVAP use cases

LISVAP repository includes test cases for both the main execution setups: EFAS and CORDEX.
These tests perform a 15 steps simulation and compare results.
You can have access to input files, base maps and XML settings files used for those tests, in case you need to examine the nature of assets.

You can easily get that data from the Docker container or just by cloning the repository.

### From Docker

For example, to copy those files from Docker image to your host (e.g. in the folder /local/folder/lisvap/input)

```bash
docker run --mount 'type=bind,src=/local/folder/lisvap/input/,dst=/input/' efas/lisvap:latest usecases
```

Alternative docker command:

```bash
docker run -v /local/folder/lisvap/input:/input efas/lisvap:latest usecases
```

Output:

```console
Copying basemaps to /input/...
copy input files to /input/cordex......
copy input files to /input/efas......
```

After executed the command, you will find data under `/local/folder/lisvap/input` directory, in two subfolders `cordex` and `efas`.


### Source code

If you clone/download LISVAP github repository, you find relevant files under `basemaps` and `tests/data` folder:

1. [input and settings files](https://github.com/ec-jrc/lisflood-lisvap/tree/master/tests/data)
2. [basemaps](https://github.com/ec-jrc/lisflood-lisvap/tree/master/basemaps)
