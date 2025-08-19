#!/bin/bash
#SBATCH --job-name=pangu
#SBATCH --partition gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=gpu:a100:1
###SBATCH --gres=gpu:v100gl:1
###SBATCH --mem=32G
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err

module purge
module load apptainer/1.3.6_gcc-11.5.0
apptainer=$(which apptainer)

cd $HOME/pangu_weather
rm -rf pangu/outputs

# Run with Apptainer and bind needed paths
srun $apptainer exec --nv \
  --bind $PWD/pangu:/workspace \
  --bind $HOME/pangu_weather/data:/data \
  $HOME/pangu_weather/run/nvidia-physicsnemo-25-03.sif \
  bash -c "cd /workspace && python train_pangu_era5.py"

#  bash -c "cd /workspace && python train_pangu_era5.py"
#  bash -c "cd /workspace && python train_pangu_lite_era5.py"
