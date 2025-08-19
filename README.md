## Data Download and Pre-Processing for Running Pangu weather on singularity.
Downloading ECMWF Reanalysis 5 (ERA5) data via the Registry on Climet Data Store(https://cds.climate.copernicus.eu/datasets) and pre-processing it for training the Pangu weather model.
## Directory structure.
- data => for train, test data.
- dataset_download => for raw data from CDS.
- pangu => for pangu weather train script with physicsnemo.
- pangu-24 => for pangu weather train script with modulus. 
- run => for run train.
## Process below.
#===============================================================
##create CDS API key and select CC-BY licence.
goto https://cds.climate.copernicus.eu/profile

$ vi ~/.cdsapirc
url: https://cds.climate.copernicus.eu/api
key: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

$ chmod 600 ~/.cdsapirc

#===============================================================
##get code.

$ git clone https://github.com/Nithiwat-S/pangu_weather.git

$ cd pangu_weather
#===============================================================
##get data.

$ mkdir -p data/zarr_data

$ module load Anaconda3/2024.10_gcc-11.5.0

$ source activate

$ conda env list

$ conda env remove --name env_xxxx

$ conda create -n env_cds-download python=3.11

$ conda activate env_cds-download

$ cd dataset_download

$ ls -al requirements.txt

$ pip install -r requirements.txt

$ cat variables_config.py.org

$ cat variables_config.py  #change zarr_store_path, hdf5_store_path and your parameter.

$ cat download_era5.py.org

$ cat download_era5.py  #change month from range(1, 13) to range(1, 3)

$ python download.py  #see data file in download_path.

$ ls -alh ../data/zarr_data/

$ python process_era5.py  #see h5 data file in write_path.

$ ls -alh ../data/train/

$ h5dump -H -A 0 ../data/train/2000.h5

$ h5ls -v ../data/train/2000.h5/params  #and see Dataset {8/8, 72/72, 721/721, 1440/1440}

open h5 file on jupyterlab

#=========================================================================
##config model (from https://github.com/NVIDIA/physicsnemo/tree/main/examples/weather/fcn_afno)

$ cd ~/fourcastnet/

$ cat fcn_afno/conf/config.yaml  #change

channels: from [0, 1, …, 19] to [0, 1] ;from Dataset

max_epoch: from 80 to 1

num_workers_train: from 8 to 1

num_workers_valida: from 8 to 1

$ cat fcn_afno/train_era5.py  #change

lr (learning rate): from 0.0005 to 0.000005

#=========================================================================
##create container and run.

$ module load apptainer/1.3.6_gcc-11.5.0

$ apptainer --version

$ cd ~/fourcastnet/run

$ cat nvidia-physicsnemo-25-03.def

$ apptainer build nvidia-physicsnemo-25-03.sif nvidia-physicsnemo-25-03.def

#or $ rsync -av --progress /lustre-home/gpu/home/research/nithiwat-r/fourcastnet/run/nvidia-physicsnemo-25-03.sif .

$ ls -alh

$$$run physicsnemo-25----------

    $ cat run_fcn_afno_1gpu1A100.sh  #edit work directory

    $ sbatch run_fcn_afno_1gpu1A100.sh

    $ squeue

    $ ls -alh

    $ cat fcn_afno-*.out  #Finished training!

$$$run modulus-24----------

    $ rsync -av --progress /lustre-home/gpu/home/research/nithiwat-r/fourcastnet/run/nvidia-modulus-24-12.sif .

    $ cat run_fcn_afno_1gpu1V100.sh  #edit work directory

    $ sbatch run_fcn_afno_1gpu1V100.sh

    $ squeue

    $ ls -alh

    $ cat fcn_afno-*.out  #Finished training!

#=========================================================================
##model output. Outputs pytorch file (.pt) will be in the checkpoints/ folder.

$ ls -alh ../fcn_afno/checkpoints  #for physicsnemo

$ ls -alh ../fcn_afno-24/checkpoints  #for modulus

rerun, delete all file in outputs directory.

$ rm -rf ../fcn_afno/outputs/*

$ rm -rf ../fcn_afno-24/outputs/*

$ sbatch run_fcn_afno_1gpu1A100.sh