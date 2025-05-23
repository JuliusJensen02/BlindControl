#!/bin/bash
#SBATCH --job-name=12/april_5_Q-Learning
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=*REDACTED*
#SBATCH --partition=naples,dhabi,rome
#SBATCH --time=192:00:00
#SBATCH --mem=5G
#SBATCH --cpus-per-task=1
#SBATCH --output=uppaal_output.log
#SBATCH --error=uppaal_error.log

cd /nfs/home/*REDACTED*/BlindControl/experiments/uppaal_jobs/job_april_12_5_Q-Learning || exit 1

for ((i=0; i<=46; i++)); do
    cp BlindModelClean.xml BlindModel.xml

    init_time=$((i*30))

    if(( i == 0 )); then
      init_temp=0.0
      init_blinds=0
      init_blocked=false
    else
        python3 -u -m get_init_data --iteration=${i}
        source init_data.sh
    fi

    sed -i "s|__INIT_TIME__|${init_time}|g" "BlindModel.xml"
    sed -i "s|__INIT_TEMP__|${init_temp}|g" "BlindModel.xml"
    sed -i "s|__BLOCKED__|${init_blocked}|g" "BlindModel.xml"
    sed -i "s|__BLINDS__|${init_blinds}|g" "BlindModel.xml"

    verifyta "BlindModel.xml" "uppaal.q" --generate-strategy=2 --learning-method=4 -u | tee "output_${i}.csv"
    python3 -u -m collect_data --iteration=${i}
done