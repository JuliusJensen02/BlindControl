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
def convert_uppaal_to_df(day: str, period: str, interval: int) -> pd.DataFrame:
    columns = ["uppaal_time", "temp_predictions_uppaal"]
    rows = []
    period = periods[period]
    start_date = datetime.strptime(period["start"], "%Y-%m-%d")
    day = (datetime.strptime(day, "%Y-%m-%d") - start_date).days
    for i in range(0, 22):
        output_file = ("experiments/uppaal_jobs/job_" +
                       str(period) + "_" +
                       str(interval) + "_" +
                       str(day) +
                       "/output_" +
                       str(period) + "_" +
                       str(interval) + "_" +
                       str(day + 1) + "_" +
                       str(i) + ".csv")
        f = open(output_file, "r")
        file_contents = f.read()
        raw_data = re.findall(r'\(([\d.]+),([\d.]+)\)', file_contents)
        buckets = defaultdict(list)
        for time, temp_predictions in raw_data:
            if time == "0" and temp_predictions == "0" and i < 0:
                continue
            int_time = int(float(time))
            buckets[int_time].append(float(temp_predictions))
        results = [(t + 60 * i, sum(temp_predictions) / len(temp_predictions)) for t, temp_predictions in buckets.items()]
        for result in results:
            rows.append([result[0], float(result[1])])

    return pd.DataFrame(rows, columns=columns)

