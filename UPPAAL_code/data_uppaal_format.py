import csv
import os
import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--file_path", required=True, type=str)
args = parser.parse_args()

def create_c_array(file_path):
    # Define paths
    #data_dir = os.path.join(os.getcwd(), "data\\1.213\query_data")

    # Define the exact filename to look for
    #data_filename = "data_2025-02-21.csv"
    #file_path = os.path.join(data_dir, data_filename)

    source_file = os.path.join(os.getcwd(), "data_arrays.c")

    # Ensure the file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Function to convert datetime string to Unix timestamp
    def convert_to_unix_timestamp(date_string):
        dt_obj = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S%z")
        return int(dt_obj.timestamp())

    # Read the CSV file
    with open(file_path, "r") as input_file:
        reader = csv.reader(input_file)
        data = [row for row in reader]

    # Skip the first row (header row)
    data = data[1:]

    # Convert date strings to Unix timestamps in each row
    for row in data:
        # Assuming the date string is in the second column (index 1)
        row[1] = str(convert_to_unix_timestamp(row[1]))

    num_rows = len(data)
    num_cols = len(data[0])

    # Write the array definition in the source file
    with open(source_file, "w") as c_file:
        c_file.write(f"const double data[{num_rows}][{num_cols}] = {{")

        # Write the data rows in the C source file
        for row in data:
            if row == data[-1]:
                c_file.write("{" + ", ".join(row) + "}")
            else:
                c_file.write("{" + ", ".join(row) + "},")
        c_file.write("};")

# Write the number of rows and columns in the C source file     
create_c_array(args.file_path)