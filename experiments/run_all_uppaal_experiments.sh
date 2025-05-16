#!/bin/bash

echo "Submitting all SLURM jobs from the 'uppaal_jobs/' directory..."

for job_script in uppaal_jobs/*/run_job.sh; do
    echo "Submitting $job_script"
    sbatch "$job_script"
done