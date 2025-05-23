#!/bin/bash
#SBATCH --job-name=job_1_213_2025_03_01_31d_240min
#SBATCH --mail-type=ALL
#SBATCH --mail-user=*REDACTED*
#SBATCH --partition=naples,dhabi,rome
#SBATCH --time=7:00:00
#SBATCH --mem=300G
#SBATCH --cpus-per-task=64
#SBATCH --output=logs_1213/output_1_213_2025_03_01_31d_240min.log
#SBATCH --error=logs_1213/error_1_213_2025_03_01_31d_240min.log
#SBATCH --exclude=rome03

cd /nfs/home/*REDACTED*/BlindControl || exit 1

python3 -u -m main_train --room='1.213' --training-start-date='2025-03-01T00:00:00Z' --training-days=31 --interval=240 --prediction-date='2025-03-16T00:00:00Z'
