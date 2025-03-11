import csv
import os
import re


data_dir = os.path.join(os.getcwd(), "..", "data")  # Go up one level to find "data"

output_file = os.path.join(os.getcwd(), "data_uppaal_format.csv")

regex_data = re.compile(r"data_\d{4}-\d{2}-\d{2}\.csv")

data_files = sorted([f for f in os.listdir(data_dir) if regex_data.match(f)])

#Open output file to store UPPAAL formatted arrays
with open(output_file, "w") as output_file:
    for data_file in data_files:
        file_path = os.path.join(data_dir, data_file)

        #Extract date from filename for naming the array
        file_name_without_extension = os.path.splitext(data_file)[0]
        array_name = file_name_without_extension.replace("-", "_")

        with open(file_path, "r") as input_file:
            reader = csv.reader(input_file)
            #rows = [",".join(row) for row in reader]
            data = [row for row in reader]

        num_rows = len(data)
        num_cols = len(data[0])

        uppaal_data = f"double {array_name}[{num_rows}][{num_cols}] = {{\n    " + ",\n    ".join(f"{{{', '.join(row)}}}" for row in data) + "\n};\n\n"

        output_file.write(uppaal_data)

print(f"UPPAAL arrays saved to {output_file}")