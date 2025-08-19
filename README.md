## Data Download and Pre-Processing for Running Pangu weather on singularity.
Downloading ECMWF Reanalysis 5 (ERA5) data via the Registry on Climet Data Store(https://cds.climate.copernicus.eu/datasets) and pre-processing it for training the Pangu weather model.
## Directory structure.
- data => for train, test data.
- dataset_download => for raw data from CDS.
- pangu => for pangu weather train script with physicsnemo.
- pangu-24 => for pangu weather train script with modulus. 
- run => for run train.
## Process below.
#=========================================================================
##get code.
$ git clone https://github.com/Nithiwat-S/pangu_weather.git
$ cd pangu_weather
#=========================================================================
##get data.

$ module load Anaconda3/2024.10_gcc-11.5.0

$ source activate

$ conda env list

$ conda env remove --name env_xxxx

$ conda create -n env_era5-download python=3.11

$ conda activate env_era5-download

$ cd aws-era5-download-script