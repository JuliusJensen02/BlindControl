import os
import re
import shutil
from datetime import datetime, timedelta

from scripts.constants import rooms, periods, prediction_intervals
from experiments.uppaal_jobs.template.data_uppaal_format import create_c_array

"""
File used to generate the different experiments carried out on the DEIS cluster. 
The experiments are defined as a date, how many days the ODE should be solved for, a prediction interval and a date that is predicted for.
"""
room = "1.213"
room_short = "1213"
method_nice_names = {
    "4": "Q-Learning",
    "5": "M-Learning",
}

for method in ["4", "5"]:
    for period_key, period in periods.items():
        for day in range(period['days']):
            for interval in prediction_intervals:
                init_alpha_a = str(rooms[room]['constants'][period_key][interval][0])
                init_alpha_s = str(rooms[room]['constants'][period_key][interval][1])
                init_alpha_h = str(rooms[room]['constants'][period_key][interval][2])
                init_alpha_v = str(rooms[room]['constants'][period_key][interval][3])
                init_alpha_o = str(rooms[room]['constants'][period_key][interval][4])
                simulation_day_date = datetime.strptime(period['start'], "%Y-%m-%d") + timedelta(days=day)
                simulation_day_date_str = simulation_day_date.strftime("%Y-%m-%d")
                c_array = create_c_array(simulation_day_date_str)

                slurm_template = """#!/bin/bash
#SBATCH --job-name="""+str(interval)+"""/"""+str(period_key)+"""_"""+str(day+1)+"""_"""+str(method_nice_names[method])+"""
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=*REDACTED*
#SBATCH --partition=naples,dhabi,rome
#SBATCH --time=192:00:00
#SBATCH --mem=5G
#SBATCH --cpus-per-task=1
#SBATCH --output=uppaal_output.log
#SBATCH --error=uppaal_error.log

cd /nfs/home/*REDACTED*/BlindControl/experiments/uppaal_jobs/job_"""+str(period_key)+"""_"""+str(interval)+"""_"""+str(day+1)+"""_"""+str(method_nice_names[method])+""" || exit 1

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

    verifyta "BlindModel.xml" "uppaal.q" --generate-strategy=2 --learning-method="""+method+""" -u | tee "output_${i}.csv"
    python3 -u -m collect_data --iteration=${i}
done"""
                os.mkdir("uppaal_jobs/job_"""+str(period_key)+"""_"""+str(interval)+"""_"""+str(day+1)+""+"""_"""+method_nice_names[method]+"")
                shutil.copyfile("uppaal_jobs/template/BlindModelClean.xml",f"uppaal_jobs/job_{period_key}_{interval}_{day+1}_{method_nice_names[method]}/BlindModelClean.xml")
                shutil.copyfile("uppaal_jobs/template/uppaalClean.q", f"uppaal_jobs/job_{period_key}_{interval}_{day+1}_{method_nice_names[method]}/uppaal.q")
                shutil.copyfile("uppaal_jobs/template/get_init_data.py", f"uppaal_jobs/job_{period_key}_{interval}_{day + 1}_{method_nice_names[method]}/get_init_data.py")
                shutil.copyfile("uppaal_jobs/template/collect_data.py", f"uppaal_jobs/job_{period_key}_{interval}_{day + 1}_{method_nice_names[method]}/collect_data.py")
                shutil.copyfile("uppaal_jobs/template/init_data.sh", f"uppaal_jobs/job_{period_key}_{interval}_{day + 1}_{method_nice_names[method]}/init_data.sh")
                shutil.copyfile("uppaal_jobs/template/accumulated_data.csv", f"uppaal_jobs/job_{period_key}_{interval}_{day + 1}_{method_nice_names[method]}/accumulated_data.csv")
                shutil.copyfile("uppaal_jobs/template/accumulated_cost.csv", f"uppaal_jobs/job_{period_key}_{interval}_{day + 1}_{method_nice_names[method]}/accumulated_cost.csv")

                query_filename = f"uppaal_jobs/job_{period_key}_{interval}_{day+1}_{method_nice_names[method]}/uppaal.q"
                model_filename = f"uppaal_jobs/job_{period_key}_{interval}_{day+1}_{method_nice_names[method]}/BlindModelClean.xml"
                with open(model_filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                updated = re.sub("__DATA__", c_array, content, flags=0)
                updated = re.sub("__ALPHA_A__", init_alpha_a, updated, flags=0)
                updated = re.sub("__ALPHA_S__", init_alpha_s, updated, flags=0)
                updated = re.sub("__ALPHA_H__", init_alpha_h, updated, flags=0)
                updated = re.sub("__ALPHA_V__", init_alpha_v, updated, flags=0)
                updated = re.sub("__ALPHA_O__", init_alpha_o, updated, flags=0)
                updated = re.sub("__PERIOD__", str(interval), updated, flags=0)

                with open(model_filename, 'w', encoding='utf-8') as f:
                    f.write(updated)

                filename = f"uppaal_jobs/job_{period_key}_{interval}_{day+1}_{method_nice_names[method]}/run_job.sh"
                with open(filename, "w", newline="\n") as f:
                    f.write(slurm_template)