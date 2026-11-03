#!/bin/bash
#SBATCH --job-name=pfsp-eo
#SBATCH --cpus-per-task=8
#SBATCH --time=01:00:00
#SBATCH --mem=8G

python main.py --procesos "$SLURM_CPUS_PER_TASK"
