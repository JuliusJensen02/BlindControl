import os

"""
File used to generate the different experiments carried out on the DEIS cluster. 
The experiments are defined as a date, how many days the ODE should be solved for, a prediction interval and a date that is predicted for.
"""
room = "1.213"
room_short = "1213"
jobs = [
    ("2024-12-01T00:00:00Z", 31, 60, "2024-12-16T00:00:00Z"),
    ("2025-01-01T00:00:00Z", 31, 60, "2025-01-16T00:00:00Z"),
    ("2025-02-01T00:00:00Z", 28, 60, "2025-02-15T00:00:00Z"),
    ("2025-03-01T00:00:00Z", 31, 60, "2025-03-16T00:00:00Z"),
    ("2024-12-01T00:00:00Z", 90, 60, "2025-01-15T00:00:00Z"),
    ("2024-12-01T00:00:00Z", 31, 240, "2024-12-16T00:00:00Z"),
    ("2025-01-01T00:00:00Z", 31, 240, "2025-01-16T00:00:00Z"),
    ("2025-02-01T00:00:00Z", 28, 240, "2025-02-15T00:00:00Z"),
    ("2025-03-01T00:00:00Z", 31, 240, "2025-03-16T00:00:00Z"),
    ("2024-12-01T00:00:00Z", 90, 240, "2025-01-15T00:00:00Z"),
    ("2024-12-01T00:00:00Z", 31, 720, "2024-12-16T00:00:00Z"),
    ("2025-01-01T00:00:00Z", 31, 720, "2025-01-16T00:00:00Z"),
    ("2025-02-01T00:00:00Z", 28, 720, "2025-02-15T00:00:00Z"),
    ("2025-03-01T00:00:00Z", 31, 720, "2025-03-16T00:00:00Z"),
    ("2024-12-01T00:00:00Z", 90, 720, "2025-01-15T00:00:00Z"),
    ("2024-12-01T00:00:00Z", 31, 1440, "2024-12-16T00:00:00Z"),
    ("2025-01-01T00:00:00Z", 31, 1440, "2025-01-16T00:00:00Z"),
    ("2025-02-01T00:00:00Z", 28, 1440, "2025-02-15T00:00:00Z"),
    ("2025-03-01T00:00:00Z", 31, 1440, "2025-03-16T00:00:00Z"),
    ("2024-12-01T00:00:00Z", 90, 1440, "2025-01-15T00:00:00Z"),
]

slurm_template = """#!/bin/bash
#SBATCH --job-name=job_{tag}
#SBATCH --mail-type=ALL
#SBATCH --mail-user=jabj22@student.aau.dk
#SBATCH --partition=naples,dhabi,rome
#SBATCH --time=7:00:00
#SBATCH --mem=300G
#SBATCH --cpus-per-task=64
#SBATCH --output=logs_{room_short}/output_{tag}.log
#SBATCH --error=logs_{room_short}/error_{tag}.log
#SBATCH --exclude=rome03

cd /nfs/home/student.aau.dk/tb30jn/BlindControl || exit 1

python3 -u -m main_args --room='{room}' --training-start-date='{start}' --training-days={days} --interval={interval} --prediction-date='{pred}'
"""

os.makedirs("jobs_" + room_short, exist_ok=True)
os.makedirs("logs_" + room_short, exist_ok=True)

for start, days, interval, pred in jobs:
    short_start = start.split("T")[0]  # "2025-01-01"
    tag = f"{room}_{short_start}_{days}d_{interval}min".replace(".", "_").replace("-", "_")
    print(tag)
    filename = f"jobs_{room_short}/job_{tag}.sh"
    with open(filename, "w", newline="\n") as f:
        f.write(slurm_template.format(
            tag=tag,
            room=room,
            start=start,
            days=days,
            interval=interval,
            pred=pred,
            room_short=room_short
        ))
