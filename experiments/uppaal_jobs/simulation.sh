#!/bin/bash
#SBATCH --job-name=job_1_231_2025_03_01_31d_240min
#SBATCH --mail-type=ALL
#SBATCH --mail-user=jabj22@student.aau.dk
#SBATCH --partition=naples,dhabi,rome
#SBATCH --time=7:00:00
#SBATCH --mem=300G
#SBATCH --cpus-per-task=64
#SBATCH --output=uppaal_output.log
#SBATCH --error=uppaal_error.log
#SBATCH --exclude=rome03

cd /nfs/home/student.aau.dk/tb30jn/uppaal/bin || exit 1

for ((i=0; i<=22; i++)); do
    init_time=$((i*60))
    cd ../../BlindControl/experiments/uppaal_jobs || exit 1
    new_name="strategy_$i.json"

    sed -i -E "s|loadStrategy[[:space:]]*\\(\"([^\"]*/)(strategy_[0-9]+\.json)\"|loadStrategy (\"\1$new_name\"|" simulation.q
    sed -i -E "s/(const int init_time = )[0-9]+;/\1$init_time;/" "BlindModel.xml"
    cd ../../../uppaal/bin || exit 1
    # Run the UPPAAL model checker
    ./verifyta.sh "../../BlindControl/experiments/uppaal_jobs/BlindModel.xml" "../../BlindControl/experiments/uppaal_jobs/simulation.q" | tee "../../BlindControl/experiments/uppaal_jobs/output_$i.csv"
done

