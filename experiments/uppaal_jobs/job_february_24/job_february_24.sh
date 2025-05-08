#!/bin/bash
#SBATCH --job-name=uppaal_strategies
#SBATCH --mail-type=ALL
#SBATCH --mail-user=jabj22@student.aau.dk
#SBATCH --partition=naples,dhabi
#SBATCH --time=7:00:00
#SBATCH --mem=300G
#SBATCH --cpus-per-task=64
#SBATCH --output=uppaal_output.log
#SBATCH --error=uppaal_error.log
#SBATCH --exclude=rome03

cd /nfs/home/student.aau.dk/tb30jn/BlindControl/experiments/uppaal_jobs/job_february_24 || exit 1
init_temp_placeholder="__INIT_TEMP__"
init_time_placeholder="__INIT_TIME__"
period_placeholder="__PERIOD__"
init_alpha_a=5.74609556e-05
init_alpha_s=5.61835875e-05
init_alpha_h=0.000308437863
init_alpha_v=0.000632119312
init_alpha_o=1.26908135e-05

for ((i=0; i<=46; i++)); do
    cp BlindModelClean.xml BlindModel.xml

    init_time=$((i*30))

    python3 -u -m data_uppaal_format --date='2025-02-17'

    data_path="data_arrays_2025-02-17.c"
    data_content=$(< "$data_path")
    escaped_data_content=$(echo "$data_content" | sed 's/[\/&\[\]\]/\&/g')
    printf '%s
' "$escaped_data_content" > data_content_2025-02-17.txt
    sed -i -E '
      /const double data\[\]\[\] = \{\};/ {
        r data_content_2025-02-17.txt
        d
      }
    ' BlindModel.xml
    
    if(( i == 0 )); then
      init_temp=0.0
      init_blinds=0
      init_blocked=false
    else
      temp_timestamp=$(grep -oE '\([0-9]+\.[0-9]+,[0-9]+\.[0-9]+\)' "output_february_24_$((i-1)).csv" | tail -n 1)
      init_temp=$(echo "$temp_timestamp" | grep -oE '[0-9]+\.[0-9]+' | tail -n 1)
      
      blocked_timestamp=$(
          grep -A1 '^blocked:' "output_february_24_$((i-1)).csv"             | tail -n1             | sed -E 's/.*\[([0-9]+)\]:.*\(([0-9]+\.[0-9]+,[0-9]+\.[0-9]+)\).*/ in ()/'
        )
        init_blocked=$(echo "$blocked_timestamp" | grep -oE '[0-9]' | tail -n 1)
        
        if (( init_blocked == 1 )); then
            init_blocked=true
        else
            init_blocked=false
        fi
        
        blinds_timestamp=$(
          grep -A1 '^blinds:' "output_february_24_$((i-1)).csv"             | tail -n1             | sed -E 's/.*\[([0-9]+)\]:.*\(([0-9]+\.[0-9]+,[0-9]+\.[0-9]+)\).*/ in ()/'
        )
        init_blinds=$(echo "$temp_timestamp" | grep -oE '[0-9]+(\.[0-9]+)?' | tail -n 1)
    fi

    sed -i "s|${period_placeholder}|24|g" "uppaal.q"
    sed -i "s|${init_time_placeholder}|${init_time}|g" "BlindModel.xml"
    sed -i "s|${init_temp_placeholder}|${init_temp}|g" "BlindModel.xml"
    
    sed -i "s|__ALPHA_A__|${init_alpha_a}|g" "BlindModel.xml"
    sed -i "s|__ALPHA_S__|${init_alpha_s}|g" "BlindModel.xml"
    sed -i "s|__ALPHA_H__|${init_alpha_h}|g" "BlindModel.xml"
    sed -i "s|__ALPHA_V__|${init_alpha_v}|g" "BlindModel.xml"
    sed -i "s|__ALPHA_O__|${init_alpha_o}|g" "BlindModel.xml"
    
    sed -i "s|__BLOCKED__|${init_blocked}|g" "BlindModel.xml"
    sed -i "s|__BLINDS__|${init_blinds}|g" "BlindModel.xml"

    verifyta "BlindModel.xml" "uppaal.q" | tee "output_february_24_${i}.csv"

    sed -i "s|24|$period_placeholder|g" "uppaal.q"

    #sed -i -E '/^const double data.*;/c\const double data[][] = {};' "BlindModel.xml"
    #sed -i -E 's|(const int init_time = )[0-9]+;|\1__INIT_TIME__;|' BlindModel.xml
    #sed -i -E 's|(const double init_temp = )[0-9]+(\.[0-9]+)?;|\1__INIT_TEMP__;|' BlindModel.xml

   
    #sed -i -E 's|(const double alpha_a = )[0-9.eE+-]+;|\1__ALPHA_A__;|' BlindModel.xml
    #sed -i -E 's|(const double alpha_s = )[0-9.eE+-]+;|\1__ALPHA_S__;|' BlindModel.xml
    #sed -i -E 's|(const double alpha_h = )[0-9.eE+-]+;|\1__ALPHA_H__;|' BlindModel.xml
    #sed -i -E 's|(const double alpha_v = )[0-9.eE+-]+;|\1__ALPHA_V__;|' BlindModel.xml
    #sed -i -E 's|(const double alpha_o = )[0-9.eE+-]+;|\1__ALPHA_O__;|' BlindModel.xml
    
    #sed -i -E 's|(bool blocked = )[0-9];|\1__BLOCKED__;|' BlindModel.xml
    #sed -i -E 's|(double blinds = )[0-9]+(\.[0-9]+)?;|\1__BLINDS__;|' BlindModel.xml
done