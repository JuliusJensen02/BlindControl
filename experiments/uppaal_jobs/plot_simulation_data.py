from collections import defaultdict
from datetime import datetime

import pandas as pd
import re
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

from scripts.data_processing import convert_csv_to_df

columns = ["time", "temp_predictions_uppaal"]
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
print(rows)

df = pd.DataFrame(rows, columns=columns)
starttime = datetime.strptime("2025-02-13", "%Y-%m-%d")
rooms = {
    "1.213": {
        "name": "1.213",
        "window_size": 3.64,
        "heater_effect": 372,
        "source_lux": "_meter"
    },
    "1.215": {
        "name": "1.215",
        "window_size": 5.46,
        "heater_effect": 422,
        "source_lux": "_meter_1.215"
    },
    "1.217": {
        "name": "1.217",
        "window_size": 3.64,
        "heater_effect": 379,
        "source_lux": "_meter"
    },
    "1.229": {
        "name": "1.229",
        "window_size": 5.18,
        "heater_effect": 758,
        "source_lux": "_meter"
    },
    "1.231": {
        "name": "1.231",
        "window_size": 6.86,
        "heater_effect": 758,
        "source_lux": "_meter"
    },
    "1.233": {
        "name": "1.233",
        "window_size": 7,
        "heater_effect": 758,
        "source_lux": "_meter"
    }
}
df2 = convert_csv_to_df(starttime, rooms["1.213"], True)
df3 = pd.merge(df, df2, how= 'left', left_index=True, right_index=True)
print(df3.head())

def plot_simulation(df):
    # Create a subplot figure with two rows
    fig = make_subplots(rows=1, cols=1, shared_xaxes=False, subplot_titles=(
        "Uppaal Temperature Predictions"))

    # First plot
    fig.add_trace(go.Scatter(x=df["time_x"], y=df["room_temp"], mode='lines', name='Temp Predictions'), row=1,
                  col=1)
    fig.add_trace(go.Scatter(x=df["time_x"], y=df["temp_predictions_uppaal"], mode='lines', name='UPPAAL'), row=1,
                  col=1)

    # Update layout
    fig.update_xaxes(title_text="Time", tickangle=45, row=1, col=1)
    fig.update_yaxes(title_text="Temperature", row=1, col=1)

    fig.update_layout(title_text="Time-Series Data (Plotly)", height=1200, width=1400)

    pio.renderers.default = "browser"
    fig.show()

plot_simulation(df3)