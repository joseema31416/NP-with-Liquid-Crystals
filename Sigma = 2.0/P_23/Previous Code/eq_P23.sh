#!/bin/sh

#SBATCH --job-name=EQP_23
#SBATCH -p gpus
#SBATCH -n 1 #### 20
#SBATCH --gres=gpu:2 ### 4 o 8
#SBATCH --time 04-00:00:00
#SBATCH --mail-type=END
#SBATCH --mail-user=eq.emmanuel.137@gmail.com

module load singularity/hoomd/2.3.5-CUDA

hoomd.python3 ramps_P23.py
