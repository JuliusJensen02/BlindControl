import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--iteration", required=True, type=int)
args = parser.parse_args()

def sanitize_line(line: str):
    return line.replace('[0]: ', '').replace('\n', '').replace('(', '').replace(')', '')

filename = "output_"+str(args.iteration)+".csv"
T_r_list = list()
H_list = list()
C_list = list()
with open(filename,'r') as csvfile:
    lines = csvfile.readlines()
    for i, line in enumerate(lines):
        if "T_r:" in line:
            sanitized_line = sanitize_line(lines[i+1])
            T_r_list = sanitized_line.split(' ')

        if "H:" in line:
            sanitized_line = sanitize_line(lines[i+1])
            H_list = sanitized_line.split(' ')

        if "C:" in line:
            sanitized_line = sanitize_line(lines[i+1])
            C_list = sanitized_line.split(' ')


        if "cost:" in line:
            sanitized_line = sanitize_line(lines[i + 1])
            cost_list = sanitized_line.split(' ')
            last_record = cost_list[-1].split(',')[1]
            cost = last_record
            with open("accumulated_cost.csv", 'r') as csvfile1:
                lines1 = csvfile1.readlines()
                acc_cost = float(lines1[0])
                acc_cost += float(cost)
                with open("accumulated_cost.csv", 'w') as csvfile2:
                    csvfile2.write(str(acc_cost))


for j, temp in enumerate(T_r_list):
    last_h_setpoint_time = 0
    last_c_setpoint_time = 0
    last_h_setpoint = None
    last_c_setpoint = None
    if j == 0:
        continue
    with open("accumulated_data.csv", 'a') as csvfile1:
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