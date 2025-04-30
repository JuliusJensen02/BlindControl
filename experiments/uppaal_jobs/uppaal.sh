#!/bin/bash
#SBATCH --job-name=uppaal_strategies
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
    python3 -u -m data_uppaal_format --file_path="../../data/1.213/query_data/data_2025-02-17.csv"

    data_path="data_arrays.c"
    data_content=$(< "$data_path")
    escaped_data_content=$(echo "$data_content" | sed 's/[\/&\[\]\\]/\\&/g')
    new_name="strategy_$i.json"

    sed -i -E "s|saveStrategy[[:space:]]*\\(\"([^\"]*/)(strategy(_[0-9])*\.json)\"|saveStrategy (\"\1$new_name\"|" query.q
    sed -i -E "s/(const int init_time = )[0-9]+;/\1$init_time;/" "BlindModel.xml"
    sed -i -E "s|const double data\[\]\[\] = \{\};|$escaped_data_content|g" "BlindModel.xml"
    cd ../../../uppaal/bin || exit 1
    # Run the UPPAAL model checker
    echo "${init_time}"
    ./verifyta.sh -O 'csv' "../../BlindControl/experiments/uppaal_jobs/BlindModel.xml" "../../BlindControl/experiments/uppaal_jobs/query.q"

    sed -i '/^const double data\[.*\] = {/,/^};/c\const double data[][] = {};' "../../BlindControl/experiments/uppaal_jobs/BlindModel.xml"
done