#!/bin/bash
#SBATCH --job-name=job_1_233_2024_12_01_90d_1440min
#SBATCH --mail-type=ALL
#SBATCH --mail-user=jabj22@student.aau.dk
#SBATCH --partition=naples,dhabi,rome
#SBATCH --time=7:00:00
#SBATCH --mem=300G
#SBATCH --cpus-per-task=64
#SBATCH --output=logs_1233/output_1_233_2024_12_01_90d_1440min.log
#SBATCH --error=logs_1233/error_1_233_2024_12_01_90d_1440min.log
#SBATCH --exclude=rome03

cd /nfs/home/student.aau.dk/tb30jn/BlindControl || exit 1

python3 -u -m main_args --room='1.233' --training-start-date='2024-12-01T00:00:00Z' --training-days=90 --interval=1440 --prediction-date='2025-01-15T00:00:00Z'
