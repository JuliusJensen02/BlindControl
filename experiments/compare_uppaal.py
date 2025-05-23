import os
rootdir = 'path\\to\\project\\BlindControl'
experimentsdir = 'path\\to\\project\\BlindControl\\experiments\\uppaal_jobs'
methods = ["Q-Learning", "M-Learning"]
intervals = [1, 4, 12, 24]
periods = ["winter", "spring", "december", "january", "february", "march", "april"]

for method in methods:
    for interval in intervals:
        for period in periods:
            highest_mem = 0
            highest_cpu_time = 0
            accumulated_cost = 0
            for day in range(1, 8):
                subdir = f"job_{period}_{interval}_{day}_{method}"
                with open(os.path.join(experimentsdir, subdir, "highest_mem_res.csv"), 'r') as memResFile:
                    highest_mem_temp = float(memResFile.read())
                    if highest_mem_temp > highest_mem:
                        highest_mem = highest_mem_temp

                with open(os.path.join(experimentsdir, subdir, "highest_cpu_time.csv"), 'r') as cpuTimeFile:
                    highest_cpu_time_temp = float(cpuTimeFile.read())
                    if highest_cpu_time_temp > highest_cpu_time:
                        highest_cpu_time = highest_cpu_time_temp

                with open(os.path.join(experimentsdir, subdir, "accumulated_cost.csv"), 'r') as costFile:
                    accumulated_cost += float(costFile.read())
            accumulated_cost /= 7
            with open(os.path.join(rootdir, f"uppaal_comp.csv"), 'a') as tempFile:
                tempFile.write(f"{method},{period},{interval},{highest_mem},{highest_cpu_time},{accumulated_cost}\n")