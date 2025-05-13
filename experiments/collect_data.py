import os
def sanitize_line(line: str):
    return line.replace('[0]: ', '').replace('\n', '').replace('(', '').replace(')', '')



rootdir = 'C:\\Users\\Julius\\PycharmProjects\\BlindControl\\experiments\\uppaal_jobs'

for subdir, dirs, files in os.walk(rootdir):
    if subdir == "template":
        continue
    os.rename(os.path.join(rootdir, subdir, "accumulated_data.py"), os.path.join(rootdir, subdir, "accumulated_data.csv"))
    for i in range(0, 47):
        with open(os.path.join(rootdir, subdir, "output_"+str(i)), 'r') as file:
            lines = csvfile.readlines()
            for i, line in enumerate(lines):
                if "T_r:" in line:
                    sanitized_line = sanitize_line(lines[i + 1])
                    temp_list = sanitized_line.split(' ')
                    for j, temp in enumerate(temp_list):
                        if j == 0 and i != 0:
                            continue
                        with open(os.path.join(rootdir, subdir, "output_"+str(i)), 'a') as csvfile:
                            csvfile.write(temp + '\n')
                    last_record = temp_list[-1].split(',')[1]
                    temp = str(last_record)
                    break