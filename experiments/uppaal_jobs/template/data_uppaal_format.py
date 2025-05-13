import csv
from datetime import datetime, timedelta

import numpy as np

def create_c_array(date):
    dt_obj1 = datetime.strptime(date, "%Y-%m-%d")
    dt_obj2 = dt_obj1 + timedelta(days=1)

    file_path1 = "../data/1.213/query_data/data_" + dt_obj1.strftime("%Y-%m-%d") + ".csv"
    file_path2 = "../data/1.213/query_data/data_" + dt_obj2.strftime("%Y-%m-%d") + ".csv"

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

    data_array_string = "const double data["+str(num_rows)+"]["+str(num_cols)+"] = {"
    for row in data:
        if np.array_equal(row, data[-1]):
            data_array_string += "{" + ", ".join(row) + "}"
        else:
            data_array_string += "{" + ", ".join(row) + "},"
    data_array_string += "};"
    return data_array_string