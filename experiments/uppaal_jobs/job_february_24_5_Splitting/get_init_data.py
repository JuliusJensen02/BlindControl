import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--iteration", required=True, type=int)
args = parser.parse_args()

def sanitize_line(line: str):
    return line.replace('[0]: ', '').replace('\n', '').replace('(', '').replace(')', '')

is_blocked = "false"
blinds = "0.0"
temp = "0.0"

filename = "output_"+str(args.iteration-1)+".csv"
with open(filename,'r') as csvfile:
    lines = csvfile.readlines()
    for i, line in enumerate(lines):
        if "blocked:" in line:
            sanitized_line = sanitize_line(lines[i+1])
            blocked_list = sanitized_line.split(' ')
            last_record = blocked_list[-1].split(',')[1]
            if last_record == '1':
                is_blocked = "true"

        if "blinds:" in line:
            sanitized_line = sanitize_line(lines[i+1])
            blinds_list = sanitized_line.split(' ')
            last_record = blinds_list[-1].split(',')[1]
            blinds = str(last_record)

        if "T_r:" in line:
            sanitized_line = sanitize_line(lines[i+1])
            temp_list = sanitized_line.split(' ')
            last_record = temp_list[-1].split(',')[1]
            temp = str(last_record)


with open("init_data.sh", "w") as f:
    f.write(f"init_blocked={is_blocked}\n")
    f.write(f"init_blinds={blinds}\n")
    f.write(f"init_temp={temp}\n")