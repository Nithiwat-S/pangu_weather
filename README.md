## Data Download and Pre-Processing for Running Pangu weather on singularity.
Downloading ECMWF Reanalysis 5 (ERA5) data via the Registry on Climet Data Store(https://cds.climate.copernicus.eu/datasets) and pre-processing it for training the Pangu weather model.
## Directory structure.
- data => for train, test data.
- dataset_download => for raw data from CDS.
- pangu => for pangu weather train script with physicsnemo.
- pangu-24 => for pangu weather train script with modulus. 
- run => for run train.
## Process below.
#========================================================================= ##get code.
$ git clone https://github.com/Nithiwat-S/pangu_weather.git

$ cd pangu_weather
#========================================================================= ##get data.

$ module load Anaconda3/2024.10_gcc-11.5.0

$ source activate

$ conda env list

$ conda env remove --name env_xxxx

$ conda create -n env_era5-download python=3.11

$ conda activate env_era5-download

$ cd aws-era5-download-script
$ ls -al requirements.txt

$ pip install -r requirements.txt

$ mkdir -p ../aws_era5_data/era5_data

$ mkdir -p ../aws_era5_data/data_processed

$ cat download.py.org

$ cat download.py  #change months = ['01']

$ cat config.yaml.org

$ cat config.yaml  #change download_path, write_path and your parameter.

$ python download.py  #see data file in download_path.

$ ls -alh ../aws_era5_data/era5_data/

$ python format.py  #see data file in write_path.

$ ls -alh ../aws_era5_data/data_processed/

$ mkdir -p ../data/train ../data/test ../data/stats

$ mv ../aws_era5_data/data_processed/2010.h5 ../data/train/

$ mv ../aws_era5_data/data_processed/2011.h5 ../data/test/

$ cat mean.py  #change path = "/mnt/fcn/data/train" and np.save path to ../data/stats.

$ python mean.py

$ cat std.py  #change path = "/mnt/fcn/data/train" and np.save path to ../data/stats.

$ python std.py

$ ls -la ../data/*/

$ h5dump -H -A 0 ../data/train/2010.h5

$ h5ls -v ../data/train/2010.h5/params  #and see Dataset {2/2}

$ open h5 file on jupyterlab

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