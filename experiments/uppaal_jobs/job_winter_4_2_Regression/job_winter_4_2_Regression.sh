#!/bin/bash
#SBATCH --job-name=4/winter_2_+Regression
#SBATCH --mail-type=ALL
#SBATCH --mail-user=jabj22@student.aau.dk
#SBATCH --partition=naples,dhabi
#SBATCH --time=192:00:00
#SBATCH --mem=25G
#SBATCH --cpus-per-task=1
#SBATCH --output=uppaal_output.log
#SBATCH --error=uppaal_error.log
#SBATCH --exclude=naples01,naples02,dhabi01,dhabi02

cd /nfs/home/student.aau.dk/tb30jn/BlindControl/experiments/uppaal_jobs/job_winter_4_2_Regression || exit 1
init_temp_placeholder="__INIT_TEMP__"
init_time_placeholder="__INIT_TIME__"
period_placeholder="__PERIOD__"
init_alpha_a=0.000162629173
init_alpha_s=1.12732988e-05
init_alpha_h=0.000522446549
init_alpha_v=0.00171810045
init_alpha_o=9.51243886e-06

for ((i=0; i<=46; i++)); do
    cp BlindModelClean.xml BlindModel.xml
    cp uppaalClean.q uppaal.q

    init_time=$((i*30))

    python3 -u -m data_uppaal_format --date='2025-02-18'

    data_path="data_arrays_2025-02-18.c"
    data_content=$(< "$data_path")
    escaped_data_content=$(echo "$data_content" | sed 's/[\/&\[\]\]/\&/g')
    printf '%s
' "$escaped_data_content" > data_content_2025-02-18.txt
    sed -i -E '
      /const double data\[\]\[\] = \{\};/ {
        r data_content_2025-02-18.txt
        d
      }
    ' BlindModel.xml
    
    if(( i == 0 )); then
      init_temp=0.0
      init_blinds=0
      init_blocked=false
    else
      temp_timestamp=$(grep -oE '\([0-9]+\.[0-9]+,[0-9]+\.[0-9]+\)' "output_winter_4_2_$((i-1)).csv" | tail -n 1)
      init_temp=$(echo "$temp_timestamp" | grep -oE '[0-9]+\.[0-9]+' | tail -n 1)
      
      blocked_timestamp=$(
          grep -A1 '^blocked:' "output_winter_4_2_$((i-1)).csv"             | tail -n1             | sed -E 's/.*\[([0-9]+)\]:.*\(([0-9]+\.[0-9]+,[0-9]+\.[0-9]+)\).*/ in ()/'
        )
        init_blocked=$(echo "$blocked_timestamp" | grep -oE '[0-9]' | tail -n 1)
        
        if (( init_blocked == 1 )); then
            init_blocked=true
        else
            init_blocked=false
        fi
        
        blinds_timestamp=$(
          grep -A1 '^blinds:' "output_winter_4_2_$((i-1)).csv"             | tail -n1             | sed -E 's/.*\[([0-9]+)\]:.*\(([0-9]+\.[0-9]+,[0-9]+\.[0-9]+)\).*/ in ()/'
        )
        init_blinds=$(echo "$temp_timestamp" | grep -oE '[0-9]+(\.[0-9]+)?' | tail -n 1)
    fi

    sed -i "s|${period_placeholder}|4|g" "uppaal.q"
    sed -i "s|__PERIOD1__|4|g" "uppaal.q"
    sed -i "s|${init_time_placeholder}|${init_time}|g" "BlindModel.xml"
    sed -i "s|${init_temp_placeholder}|${init_temp}|g" "BlindModel.xml"
    
    sed -i "s|__ALPHA_A__|${init_alpha_a}|g" "BlindModel.xml"
    sed -i "s|__ALPHA_S__|${init_alpha_s}|g" "BlindModel.xml"
    sed -i "s|__ALPHA_H__|${init_alpha_h}|g" "BlindModel.xml"
    sed -i "s|__ALPHA_V__|${init_alpha_v}|g" "BlindModel.xml"
    sed -i "s|__ALPHA_O__|${init_alpha_o}|g" "BlindModel.xml"
    
    sed -i "s|__BLOCKED__|${init_blocked}|g" "BlindModel.xml"
    sed -i "s|__BLINDS__|${init_blinds}|g" "BlindModel.xml"

    verifyta "BlindModel.xml" "uppaal.q" --generate-strategy=1 --learning-method=2 --exploration=1 | tee "output_winter_4_2_${i}.csv"
done