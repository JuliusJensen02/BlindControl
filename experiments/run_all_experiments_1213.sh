#!/bin/bash

echo "Submitting all SLURM jobs from the 'jobs_1213/' directory..."

for job_script in jobs_1213/job_*.sh; do
    echo "Submitting $job_script"
    sbatch "$job_script"
done