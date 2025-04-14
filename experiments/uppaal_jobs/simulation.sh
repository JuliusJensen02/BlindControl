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
  for ((j=17; j<=21; j++)); do
    init_time=$((i*60))
    cd ../../BlindControl/experiments/uppaal_jobs || exit 1

    if(( i == 0 )); then
      init_temp=0.0
    else
      temp_timestamp=$(grep -oE '\([0-9]+\.[0-9]+,[0-9]+\.[0-9]+\)' "output_2025_02_${j}_$((i-1)).csv" | tail -n 1)
      init_temp=$(echo "$temp_timestamp" | grep -oE '[0-9]+\.[0-9]+' | tail -n 1)
    fi

    new_name="strategy_$i.json"
    sed -i -E "s|loadStrategy[[:space:]]*\\(\"([^\"]*/)(strategy_[0-9]+\.json)\"|loadStrategy (\"\1$new_name\"|" simulation.q
    sed -i -E "s/(const int init_time = )[0-9]+;/\1$init_time;/" "BlindModel_1213_2025_02_${j}.xml"
    sed -i -E "s/(const double init_temp = )[0-9]+\.[0-9]+;/\1$init_temp;/" "BlindModel_1213_2025_02_${j}.xml"
    cd ../../../uppaal/bin || exit 1
    # Run the UPPAAL model checker
    ./verifyta.sh "../../BlindControl/experiments/uppaal_jobs/BlindModel_1213_2025_02_${j}.xml" "../../BlindControl/experiments/uppaal_jobs/simulation.q" | tee "../../BlindControl/experiments/uppaal_jobs/output_2025_02_${j}_${i}.csv"
  done
done

