from collections import defaultdict
from datetime import datetime

import pandas as pd
import re
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

from scripts.data_processing import convert_csv_to_df


def convert_uppaal_to_df():
    columns = ["uppaal_time", "temp_predictions_uppaal"]
    rows = []

    for i in range(0, 22):
        f = open("experiments/uppaal_jobs/output_" + str(i) + ".csv", "r")
        file_contents = f.read()
        raw_data = re.findall(r'\(([\d.]+),([\d.]+)\)', file_contents)
        buckets = defaultdict(list)
        for time, temp_predictions in raw_data:
            int_time = int(float(time))
            buckets[int_time].append(float(temp_predictions))
        results = [(t + 60 * i, sum(temp_predictions) / len(temp_predictions)) for t, temp_predictions in buckets.items()]
        for result in results:
            rows.append([result[0], float(result[1])])

    return pd.DataFrame(rows, columns=columns)


def plot_simulation(df):
    # Create a subplot figure with two rows
    fig = make_subplots(rows=1, cols=1, shared_xaxes=False, subplot_titles=(
        "Uppaal Temperature Predictions"))

    # First plot
    fig.add_trace(go.Scatter(x=df["time_x"], y=df["room_temp"], mode='lines', name='Room Temperature'), row=1,
                  col=1)
    fig.add_trace(go.Scatter(x=df["time_x"], y=df["temp_predictions_uppaal"], mode='lines', name='UPPAAL'), row=1,
                  col=1)
    fig.add_trace(go.Scatter(x=df["time_x"], y=df["heating_setpoint"], mode='lines', name='Heating Setpoint'), row=1,
                  col=1)
    fig.add_trace(go.Scatter(x=df["time_x"], y=df["cooling_setpoint"], mode='lines', name='Cooling Setpoint'), row=1,
                  col=1)

    # Update layout
    fig.update_xaxes(title_text="Time", tickangle=45, row=1, col=1)
    fig.update_yaxes(title_text="Temperature", row=1, col=1)

    fig.update_layout(title_text="Time-Series Data (Plotly)", height=1200, width=1800)

    pio.renderers.default = "browser"
    fig.show()

