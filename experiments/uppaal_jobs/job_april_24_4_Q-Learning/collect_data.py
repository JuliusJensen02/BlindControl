import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--iteration", required=True, type=int)
args = parser.parse_args()

def sanitize_line(line: str):
    return line.replace('[0]: ', '').replace('\n', '').replace('(', '').replace(')', '')

filename = "output_"+str(args.iteration)+".csv"
with open(filename,'r') as csvfile:
    lines = csvfile.readlines()
    for i, line in enumerate(lines):
        if "T_r:" in line:
            sanitized_line = sanitize_line(lines[i+1])
            temp_list = sanitized_line.split(' ')
            for j, temp in enumerate(temp_list):
                if j == 0 and i != 0:
                    continue
                with open("accumulated_data.csv", 'a') as csvfile1:
                    index = float(temp.split(',')[0]) + 30 * args.iteration
                    temp = temp.split(',')[1]

                    csvfile1.write(str(index) + ',' + temp + '\n')

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
