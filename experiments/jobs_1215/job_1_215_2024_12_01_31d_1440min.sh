#!/bin/bash
#SBATCH --job-name=job_1_215_2024_12_01_31d_1440min
#SBATCH --mail-type=ALL
#SBATCH --mail-user=jabj22@student.aau.dk
#SBATCH --partition=naples,dhabi,rome
#SBATCH --time=7:00:00
#SBATCH --mem=300G
#SBATCH --cpus-per-task=64
#SBATCH --output=logs_1215/output_1_215_2024_12_01_31d_1440min.log
#SBATCH --error=logs_1215/error_1_215_2024_12_01_31d_1440min.log
#SBATCH --exclude=rome03

cd /nfs/home/student.aau.dk/tb30jn/BlindControl || exit 1

python3 -u -m main_args --room='1.215' --training-start-date='2024-12-01T00:00:00Z' --training-days=31 --interval=1440 --prediction-date='2024-12-16T00:00:00Z'
