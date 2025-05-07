import re
from pathlib import Path

root_path = Path('experiments/')
pattern_folder = re.compile(r'^logs_1213$')
pattern_logs = re.compile(r'^output_\d_\d{3}_\d{4}_\d{2}_\d{2}_\d{2}d_\d{1,5}min$')
with open("experiment_data.csv", 'w') as f:
    f.write("Period,Hours,Room,Error,Constants\n")
    f.close()

for folder in root_path.iterdir():
    if folder.is_dir() and pattern_folder.match(folder.name):
        print(f"Running for: {folder.name}")
        for file in folder.iterdir():
            if file.is_file() and pattern_logs.match(file.stem):
                print(file.name)
                with (open(file, 'r') as f):
                    file_contents = f.read()
                    file_contents = file_contents.replace('\n', ' ')
                    constants = re.search(r'\[([^]]+)]', file_contents).group(1)
                    constants = re.findall(r'\d\.\d{1,20}e-\d{2}', constants)
                    error = re.search(r']\s*([0-9.eE+-]+)', file_contents).group(1)
                    file_name_atoms = file.stem.split("_")
                    if file_name_atoms[3] == "2024" and file_name_atoms[4] == "12" and file_name_atoms[5] == "01" and file_name_atoms[6] == "31d":
                        period = "December"
                    elif file_name_atoms[3] == "2025" and file_name_atoms[4] == "01" and file_name_atoms[5] == "01":
                        period = "January"
                    elif file_name_atoms[3] == "2025" and file_name_atoms[4] == "02" and file_name_atoms[5] == "01":
                        period = "February"
                    elif file_name_atoms[3] == "2025" and file_name_atoms[4] == "03" and file_name_atoms[5] == "01" and file_name_atoms[6] == "31d":
                        period = "March"
                    elif file_name_atoms[3] == "2025" and file_name_atoms[4] == "04" and file_name_atoms[5] == "01":
                        period = "April"
                    elif file_name_atoms[3] == "2024" and file_name_atoms[4] == "12" and file_name_atoms[5] == "01" and file_name_atoms[6] == "90d":
                        period = "Winter"
                    elif file_name_atoms[3] == "2025" and file_name_atoms[4] == "03" and file_name_atoms[5] == "01" and file_name_atoms[6] == "61d":
                        period = "Spring"

                    if file_name_atoms[7] == "60min":
                        hours = "1"
                    elif file_name_atoms[7] == "240min":
                        hours = "4"
                    elif file_name_atoms[7] == "720min":
                        hours = "12"
                    elif file_name_atoms[7] == "1440min":
                        hours = "24"

                    room = file_name_atoms[1] + "." + file_name_atoms[2]
                    with open("experiment_data.csv", 'a') as f:
                        line = period + "," + hours + "," + room + "," + error + "," + "\"[" + constants[0] + ", " + constants[1] + ", " + constants[2] + ", " + constants[3] + ", " + constants[4] + "]\"" + "\n"
                        f.write(line)
