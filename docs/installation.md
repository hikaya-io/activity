# Installation

> TODO detailed installation guide

1. Development setup with hot reload
2. Python virtual environment and dependencies installation
3. Django config file & Django "superuser" creation
4. Running migrations & fixtures
5. Gaining access to local Activity instance


## Install non-python dependencies

1. **GDAL**

On MacOs:

```bash
$ brew install gdal
```

On Windows:
- You will need to download Gdal Core and Gdal installer for your version of Python.
- Please read the following [instructions](https://pypi.org/project/GDAL/#windows) on how to properly install and test gdal.

2. **Pango**

On MacOs:

```bash
$ brew install pango
```

On Windows:
- You will need Pango and Cairo for the application to run.
- The runtime installer can be found [here](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases)
- Download and install GTK+-3. 
