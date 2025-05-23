import os
from collections import defaultdict
from datetime import datetime

from scripts.constants import periods

import pandas as pd
import re

"""
Function that takes the temperature predictions from UPPAAL simulations and converts
them to a dataframe.
Args:
    day: String of the date.
Returns:
    A dataframe containing the temperature predictions from UPPAAL simulations.
"""
def convert_uppaal_to_df(day: int, period: str, interval: int, method: str) -> pd.DataFrame:
    columns = ["time", "temp_predictions", "heating_setpoint", "cooling_setpoint"]
    rows = []
    rootdir = 'path\\to\\project\\BlindControl\\experiments\\uppaal_jobs'

    with open(os.path.join(rootdir, "job_"+period+"_"+str(interval)+"_"+str(day)+"_"+method, "accumulated_data.csv"), 'r') as dataFile:
        lines = dataFile.readlines()
        for line in lines:
            time = float(line.split(",")[0])
            temp_predictions = float(line.split(",")[1])
            heating_setpoint = float(line.split(",")[2])
            cooling_setpoint = float(line.split(",")[3])
            rows.append([time, temp_predictions, heating_setpoint, cooling_setpoint])

    return pd.DataFrame(rows, columns=columns)

