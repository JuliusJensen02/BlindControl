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

cd /nfs/home/student.aau.dk/tb30jn/BlindControl/experiments/uppaal_jobs || exit 1
init_temp_placeholder="__INIT_TEMP__"
init_time_placeholder="__INIT_TIME__"

for ((i=0; i<=22; i++)); do
  for ((j=17; j<=21; j++)); do
    init_time=$((i*60))
    python3 -u -m data_uppaal_format --file_path="../../data/1.213/query_data/data_2025-02-${j}.csv"

    data_path="data_arrays.c"
    data_content=$(< "$data_path")
    escaped_data_content=$(echo "$data_content" | sed 's/[\/&\[\]\\]/\\&/g')

    if(( i == 0 )); then
      init_temp=0.0
    else
      temp_timestamp=$(grep -oE '\([0-9]+\.[0-9]+,[0-9]+\.[0-9]+\)' "output_2025_02_${j}_$((i-1)).csv" | tail -n 1)
      init_temp=$(echo "$temp_timestamp" | grep -oE '[0-9]+\.[0-9]+' | tail -n 1)
    fi

    new_name="strategy_$i.json"

    sed -i -E "s|loadStrategy[[:space:]]*\\(\"([^\"]*/)(strategy(_[0-9])*\.json)\"|loadStrategy (\"\1$new_name\"|" simulation.q
    sed -i -E "s|const double data\[\]\[\] = \{\};|$escaped_data_content|g" "BlindModel.xml"
    sed -i "s|$init_time_placeholder|$init_time|g" "BlindModel.xml"
    sed -i "s|$init_temp_placeholder|$init_temp|g" "BlindModel.xml"

    # Run the UPPAAL model checker
    cd ../../../uppaal/bin || exit 1
    ./verifyta.sh "../../BlindControl/experiments/uppaal_jobs/BlindModel.xml" "../../BlindControl/experiments/uppaal_jobs/simulation.q" | tee "../../BlindControl/experiments/uppaal_jobs/output_2025_02_${j}_${i}.csv"
    cd ../../BlindControl/experiments/uppaal_jobs || exit 1

    sed -i '/^const double data\[.*\] = {/,/^};/c\const double data[][] = {};' "BlindModel.xml"
    sed -i -E "s/(const int init_time = )$init_time;/\1$init_time_placeholder;/" "BlindModel.xml"
    sed -i -E "s/(const double init_temp = )$init_temp;/\1$init_temp_placeholder;/" "BlindModel.xml"
  done
done



