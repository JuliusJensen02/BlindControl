import csv
import os
import argparse
from datetime import datetime, timedelta

import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--date", required=True, type=str)
args = parser.parse_args()

def create_c_array(date):

    source_file = os.path.join(os.getcwd(), "data_arrays_"+date+".c")


    dt_obj1 = datetime.strptime(date, "%Y-%m-%d")
    dt_obj2 = dt_obj1 + timedelta(days=1)

    file_path1 = "../../../data/1.213/query_data/data_" + dt_obj1.strftime("%Y-%m-%d") + ".csv"
    file_path2 = "../../../data/1.213/query_data/data_" + dt_obj2.strftime("%Y-%m-%d") + ".csv"

    data = []
    # Read the CSV file
    with open(file_path1, "r") as input_file:
        reader = csv.reader(input_file)
        next(reader, None)
        for row in reader:
            data.append(row)
    with open(file_path2, "r") as input_file:
        reader = csv.reader(input_file)
        next(reader, None)
        for row in reader:
            data.append(row)

    data = np.array(data)
    data = data[:, 2:]

    num_rows = len(data)
    num_cols = len(data[0])

    # Write the array definition in the source file
    with open(source_file, "w") as c_file:
        c_file.write(f"const double data[{num_rows}][{num_cols}] = {{")

        # Write the data rows in the C source file
        for row in data:
            if np.array_equal(row, data[-1]):
                c_file.write("{" + ", ".join(row) + "}")
            else:
                c_file.write("{" + ", ".join(row) + "},")
        c_file.write("};")

# Write the number of rows and columns in the C source file     
create_c_array(args.date)