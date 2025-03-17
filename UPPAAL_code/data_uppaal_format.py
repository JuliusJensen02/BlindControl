import csv
import os
import re
from datetime import datetime

data_dir = os.path.join(os.getcwd(), "data")  # Go up one level to find "data"
header_file = os.path.join(os.getcwd(), "UPPAAL_code/data_arrays.h")
source_file = os.path.join(os.getcwd(), "UPPAAL_code/data_arrays.c")

regex_data = re.compile(r"data_\d{4}-\d{2}-\d{2}\.csv")

data_files = sorted([f for f in os.listdir(data_dir) if regex_data.match(f)])


# Function to convert datetime string to Unix timestamp
def convert_to_unix_timestamp(date_string):
    # Parse the datetime string (assuming the format is 'YYYY-MM-DD HH:MM:SS+TZ')
    dt_obj = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S%z")
    # Return Unix timestamp
    return int(dt_obj.timestamp())

# Open the header file to store the array declarations
with open(header_file, "w") as h_file:
    # Write the header content
    h_file.write("#ifndef DATA_ARRAYS_H\n")
    h_file.write("#define DATA_ARRAYS_H\n\n")
    h_file.write("#include <stdint.h>\n\n")  # Include necessary libraries

    for data_file in data_files:
        file_path = os.path.join(data_dir, data_file)

        # Extract date from filename for naming the array
        file_name_without_extension = os.path.splitext(data_file)[0]
        array_name = file_name_without_extension.replace("-", "_")

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

        # Write the array declaration in the header file
        h_file.write(f"extern double {array_name}[{num_rows}][{num_cols}];\n")

    h_file.write("\n#endif // DATA_ARRAYS_H\n")

# Open the source file to store the array definitions
with open(source_file, "w") as c_file:
    # Include the header at the top of the C source file
    c_file.write("#include \"data_arrays.h\"\n\n")

    for data_file in data_files:
        file_path = os.path.join(data_dir, data_file)

        # Extract date from filename for naming the array
        file_name_without_extension = os.path.splitext(data_file)[0]
        array_name = file_name_without_extension.replace("-", "_")

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
        c_file.write(f"double {array_name}[{num_rows}][{num_cols}] = {{\n")

        # Write the data rows in the C source file
        for row in data:
            c_file.write("    {" + ", ".join(row) + "},\n")

        # Close the array definition
        c_file.write("};\n\n")

