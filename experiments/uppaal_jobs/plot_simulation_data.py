from collections import defaultdict
from datetime import datetime

import pandas as pd
import re
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

from scripts.data_processing import convert_csv_to_df

"""
Function that takes the temperature predictions from UPPAAL simulations and converts
them to a dataframe.
Args:
    day: String of the date.
Returns:
    A dataframe containing the temperature predictions from UPPAAL simulations.
"""
def convert_uppaal_to_df(day: str) -> pd.DataFrame:
    columns = ["uppaal_time", "temp_predictions_uppaal"]
    rows = []

    for i in range(0, 22):
        f = open("experiments/uppaal_logs/output_"+day+"_" + str(i) + ".csv", "r")
        file_contents = f.read()
        raw_data = re.findall(r'\(([\d.]+),([\d.]+)\)', file_contents)
        buckets = defaultdict(list)
        for time, temp_predictions in raw_data:
            if time == "0" and temp_predictions == "0":
                continue
            int_time = int(float(time))
            buckets[int_time].append(float(temp_predictions))
        results = [(t + 60 * i, sum(temp_predictions) / len(temp_predictions)) for t, temp_predictions in buckets.items()]
        for result in results:
            rows.append([result[0], float(result[1])])

    return pd.DataFrame(rows, columns=columns)

