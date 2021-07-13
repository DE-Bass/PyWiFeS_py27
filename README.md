# PyWiFeS

modified by ___jhwshin___

Python Packages and PATHS are contained within the python virtual environment pipeline for modularity.

---

## Requirements:
* `python3`
* `pip`

---

## ENV Setup:

0. Create a python virtual environment:

```bash
$   python -m venv venv
```

1. Patch `activate` to add `pipeline/{src,reduction_scripts}` to `PYTHONPATHS` in venv:

```bash
$   patch -u venv/bin/activate -i pypaths.patch
```

2. Create shortcut to `activate` venv:

```bash
$   ln -sv venv/bin/activate .
```

3. Activate to start the python venv:

```bash
$   source activate
```

4. Upgrade `pip` to latest version:

```bash
$   pip install --upgrade pip
```

5. Install required packages with `pip`:

```bash
$   pip install -r requirements.txt
```

---

To __EXIT__ the venv simply type:

```bash
$   deactivate
```

To __START__ the environment again type:

```bash
$   source activate
```

---

## Pipeline Instructions:

0. All files are contained within `template` folder, copy it and rename to any workspace name:

```bash
$   cp template <NAME>
$   cp <PATH_TO_FITS>/*.fits <NAME>/raw_data
```

1. Generate metadata from raw `fits` files:

```bash
$   python2 generate_metadata_script.py raw_data
```

* __raw_data__ dir containing `*.fits` files

> Outputs: `save_{blue,red}_metadata.py` files

2. Create pickle files:

```bash
$   python2 save_{red,blue}_metadata.py
```

> Outputs: `wifes{B,R}_.*_metadata.pkl` files

3. Run `reduce_{blue,red}`

```bash
$   python2 reduce_{blue,red} wifes{B,R}_.*_metadata.pkl
```

* Or run this command for sanitised output with log file:
```bash
$   python2 -u -W ignore reduce_{blue,red} wifes{B,R}_.*_metadata.pkl 2>&1 | tee log.txt

# USEFUL COMMANDS:

# -u              unbuffered prints immediately (otherwise will print sporadically with tee)
# -W ignore       ignore Warnings
# 2>&1            prints stderr to stdout (used for tee)
```

---

## Changes / Fixes:

### Fixes:
* new `reference_data` from latest origin `PyWiFeS` in `github`
* rename all `reference_data` files to `.tab` as well as `stdstar_lookup_table` for consistency
* fixed some bugs in `src/wifi_calib.py` when searching for star `ref_names`
* renamed `template` folder and added default `reduc_{b,r}` folder

### Features:
* now running pipeline in `pyvenv` for better abstraction with contained packages and pythonpaths
* added `sort.py `as a manual inspection tool
* added this `README`
