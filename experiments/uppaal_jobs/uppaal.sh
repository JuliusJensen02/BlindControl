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

cd /nfs/home/student.aau.dk/tb30jn/BlindControl/experiments/uppaal_jobs || exit 1
init_temp_placeholder="__INIT_TEMP__"
init_time_placeholder="__INIT_TIME__"

for ((i=0; i<=22; i++)); do
    init_time=$((i*60))

    python3 -u -m data_uppaal_format --file_path="../../data/1.213/query_data/data_2025-02-17.csv"

    data_path="data_arrays.c"
    data_content=$(< "$data_path")
    escaped_data_content=$(echo "$data_content" | sed 's/[\/&\[\]\\]/\\&/g')
    new_name="strategy_$i.json"

    sed -i -E "s|saveStrategy[[:space:]]*\\(\"([^\"]*/)(strategy(_[0-9])*\.json)\"|saveStrategy (\"\1$new_name\"|" query.q
    sed -i -E "s|const double data\[\]\[\] = \{\};|$escaped_data_content|g" "BlindModel.xml"
    sed -i "s|$init_time_placeholder|$init_time|g" "BlindModel.xml"
    sed -i "s|$init_temp_placeholder|0.0|g" "BlindModel.xml"

    verifyta -O 'csv' "BlindModel.xml" "query.q"

    sed -i '/^const double data\[.*\] = {/,/^};/c\const double data[][] = {};' "BlindModel.xml"
    sed -i -E "s/(const int init_time = )$init_time;/\1__INIT_TIME__;/" "BlindModel.xml"
    sed -i -E "s/(const double init_temp = )0.0;/\1__INIT_TEMP__;/" "BlindModel.xml"
done