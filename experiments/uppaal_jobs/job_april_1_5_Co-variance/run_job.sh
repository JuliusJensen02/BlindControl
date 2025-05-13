#!/bin/bash
#SBATCH --job-name=1/april_5_Co-variance
#SBATCH --mail-type=ALL
#SBATCH --mail-user=jabj22@student.aau.dk
#SBATCH --partition=naples,dhabi
#SBATCH --time=192:00:00
#SBATCH --mem=25G
#SBATCH --cpus-per-task=1
#SBATCH --output=uppaal_output.log
#SBATCH --error=uppaal_error.log
#SBATCH --exclude=naples01,naples02,dhabi01,dhabi02

cd /nfs/home/student.aau.dk/tb30jn/BlindControl/experiments/uppaal_jobs/job_april_1_5_Co-variance || exit 1

for ((i=0; i<=46; i++)); do
    cp BlindModelClean.xml BlindModel.xml
    cp uppaalClean.q uppaal.q

    init_time=$((i*30))

    if(( i == 0 )); then
      init_temp=0.0
      init_blinds=0
      init_blocked=false
    else
        python3 -u -m get_init_data --iteration=${i}
        source init_data.sh
    fi

    sed -i "s|__PERIOD__|1|g" "uppaal.q"
    sed -i "s|__PERIOD1__|1|g" "uppaal.q"
    sed -i "s|__INIT_TIME__|${init_time}|g" "BlindModel.xml"
    sed -i "s|__INIT_TEMP__|${init_temp}|g" "BlindModel.xml"
    
    sed -i "s|__BLOCKED__|${init_blocked}|g" "BlindModel.xml"
    sed -i "s|__BLINDS__|${init_blinds}|g" "BlindModel.xml"

    verifyta "BlindModel.xml" "uppaal.q" --generate-strategy=1 --learning-method=0 -u | tee "output_${i}.csv"
done