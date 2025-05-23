import os

def sanitize_line(line: str):
    return line.replace('[0]: ', '').replace('\n', '').replace('(', '').replace(')', '')

rootdir = 'path\\to\\project\\BlindControl\\experiments\\uppaal_jobs'

for subdir, dirs, files in os.walk(rootdir):
    for subdir1 in dirs:
        if "job" not in subdir1:
            continue

        T_r_list = list()
        H_list = list()
        C_list = list()
        highest_mem_vir = 0
        highest_mem_res = 0
        highest_cpu_time = 0
        found_temp = True
        with open(os.path.join(rootdir, subdir1, "accumulated_data.csv"), 'w') as tempFile:
            print(subdir1)

        for i in range(0, 47):
            temp_found_temp = False
            with open(os.path.join(rootdir, subdir1, "output_"+str(i))+".csv", 'r') as csvfile:
                lines = csvfile.readlines()
                for j, line in enumerate(lines):
                    if "T_r:" in line:
                        sanitized_line = sanitize_line(lines[j + 1])
                        T_r_list = sanitized_line.split(' ')
                        if len(T_r_list) >= 2 or i == 46:
                            temp_found_temp = True
                    if "H:" in line:
                        sanitized_line = sanitize_line(lines[j + 1])
                        H_list = sanitized_line.split(' ')

                    if "C:" in line:
                        sanitized_line = sanitize_line(lines[j + 1])
                        C_list = sanitized_line.split(' ')
                    if "-- CPU user time used :" in line:
                        cleanLine = line.replace(" ", "")
                        cpu_time = float(line.split(":")[1].split("m")[0])
                        if cpu_time > highest_cpu_time:
                            highest_cpu_time = cpu_time
                    if "-- Virtual memory used :" in line:
                        cleanLine = line.replace(" ", "")
                        mem_vir = float(line.split(":")[1].split("K")[0])
                        if mem_vir > highest_mem_vir:
                            highest_mem_vir = mem_vir

                    if "-- Resident memory used :" in line:
                        cleanLine = line.replace(" ", "")
                        mem_res = float(line.split(":")[1].split("K")[0])
                        if mem_res > highest_mem_res:
                            highest_mem_res = mem_res
            if not temp_found_temp:
                found_temp = False
            for j, temp in enumerate(T_r_list):
                last_h_setpoint_time = 0
                last_c_setpoint_time = 0
                last_h_setpoint = None
                last_c_setpoint = None
                if j == 0:
                    continue
                with open(os.path.join(rootdir, subdir1, "accumulated_data.csv"), 'a') as csvfile1:
                    index = float(temp.split(',')[0]) + 30 * i
                    temp = temp.split(',')[1]
                    for k in range(0, len(H_list)):
                        if H_list[k].split(',')[0] >= temp.split(',')[0]:
                            last_h_setpoint_time = H_list[k].split(',')[1]
                            last_h_setpoint = H_list[k].split(',')[1]

                    for k in range(0, len(C_list)):
                        if C_list[k].split(',')[0] >= temp.split(',')[0]:
                            last_c_setpoint_time = C_list[k].split(',')[1]
                            last_c_setpoint = C_list[k].split(',')[1]

                    csvfile1.write(str(index) + ',' + str(temp) + ',' + str(last_h_setpoint) + ',' + str(last_c_setpoint) + '\n')
        if not found_temp:
            print("No temperature data found in " + str(subdir1))

        with open(os.path.join(rootdir, subdir1, "highest_mem_vir.csv"), 'w') as memVirFile:
            memVirFile.write(str(highest_mem_vir))
        with open(os.path.join(rootdir, subdir1, "highest_mem_res.csv"), 'w') as memResFile:
            memResFile.write(str(highest_mem_res))
        with open(os.path.join(rootdir, subdir1, "highest_cpu_time.csv"), 'w') as cpuTimeFile:
            cpuTimeFile.write(str(highest_cpu_time))
    break