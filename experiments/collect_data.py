import os

rootdir = 'C:\\Users\\Julius\\PycharmProjects\\BlindControl\\experiments\\uppaal_jobs'

for subdir, dirs, files in os.walk(rootdir):
    for subdir1 in dirs:
        if "job" not in subdir1:
            continue
        highest_mem_vir = 0
        highest_mem_res = 0
        highest_cpu_time = 0

        for i in range(0, 47):
            with open(os.path.join(rootdir, subdir1, "output_"+str(i))+".csv", 'r') as csvfile:
                lines = csvfile.readlines()
                for j, line in enumerate(lines):
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
        with open(os.path.join(rootdir, subdir1, "highest_mem_vir.csv"), 'w') as memVirFile:
            memVirFile.write(str(highest_mem_vir))
        with open(os.path.join(rootdir, subdir1, "highest_mem_res.csv"), 'w') as memResFile:
            memResFile.write(str(highest_mem_res))
        with open(os.path.join(rootdir, subdir1, "highest_cpu_time.csv"), 'w') as cpuTimeFile:
            cpuTimeFile.write(str(highest_cpu_time))
    break