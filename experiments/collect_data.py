import os
def sanitize_line(line: str):
    return line.replace('[0]: ', '').replace('\n', '').replace('(', '').replace(')', '')



rootdir = 'C:\\Users\\Julius\\PycharmProjects\\BlindControl\\experiments\\uppaal_jobs'

for subdir, dirs, files in os.walk(rootdir):
    for subdir1 in dirs:
        if "job" not in subdir1:
            continue
        if os.path.isfile(os.path.join(rootdir, subdir1, "accumulated_data.py")):
            os.rename(os.path.join(rootdir, subdir1, "accumulated_data.py"), os.path.join(rootdir, subdir1, "accumulated_data.csv"))
        with open(os.path.join(rootdir, subdir1, "accumulated_data.csv"), 'w') as csvfile:
            print("Reset "+os.path.join(rootdir, subdir1, "accumulated_data.csv"))
        for i in range(0, 47):
            with open(os.path.join(rootdir, subdir1, "output_"+str(i))+".csv", 'r') as csvfile:
                lines = csvfile.readlines()
                for j, line in enumerate(lines):
                    if "T_r:" in line:
                        sanitized_line = sanitize_line(lines[j + 1])
                        temp_list = sanitized_line.split(' ')
                        for k, temp in enumerate(temp_list):
                            if k == 0 and i != 0:
                                continue
                            with open(os.path.join(rootdir, subdir1, "accumulated_data.csv"), 'a') as csvfile1:
                                csvfile1.write(temp + '\n')
                        break
    break