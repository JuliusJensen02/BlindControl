import csv
import os
from datetime import datetime

# Define paths
data_dir = os.path.join(os.getcwd(), "data\\1.213\query_data")
source_file = os.path.join(os.getcwd(), "UPPAAL_code/data_arrays.c")

# Define the exact filename to look for
data_filename = "data_2025-02-21.csv"
file_path = os.path.join(data_dir, data_filename)

# Ensure the file exists
if not os.path.isfile(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")

"""
Function to convert datetime string to Unix timestamp.
Args: 
    date_string: A string of the date in datetime format.
Returns: 
    A int object representing the unix timestamp.
"""
def convert_to_unix_timestamp(date_string: str) -> int:
    dt_obj = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S%z")
    return int(dt_obj.timestamp())

# Extract date from filename for naming the array
file_name_without_extension = os.path.splitext(data_filename)[0]
array_name = "data"

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
    c_file.write(f"const double {array_name}[{num_rows}][{num_cols}] = {{\n")

    # Write the data rows in the C source file
    for row in data:
        c_file.write("    {" + ", ".join(row) + "},\n")

    c_file.write("};\n\n")
