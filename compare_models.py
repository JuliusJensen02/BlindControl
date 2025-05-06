from datetime import datetime

import pandas as pd

from main import rooms

from data_processing import get_raw_data_as_df




import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots


def V_valve(c_s: float, T: float) -> float:
    ventilation_valve = 0.3
    if T > c_s:
        ventilation_valve = 1

    return ventilation_valve


def convert_v_value(valve: float) -> float:
    min_raw, max_raw = 0, 100
    min_act, max_act = 30, 100

    return (
            (valve - min_raw)
            / (max_raw - min_raw)
            * (max_act - min_act)
            + min_act
    )


def H_valve(h_s: float, T: float) -> float:
    heater_valve = 0
    if T <= h_s:
        heater_valve = 1

    return heater_valve


dt = datetime(2025, 3, 3, 0, 0, 0)
data = get_raw_data_as_df(dt, rooms["1.213"])
calculated_data = list()
for row in data.itertuples(index=False):

    calculated_data.append({
        "room_temp": row.room_temp,
        "heating_setpoint": row.heating_setpoint,
        "cooling_setpoint": row.cooling_setpoint,
        "time": row.time,
        "V_valve_actual": convert_v_value(row.ventilation_supply_damper)/100,
        "H_valve_actual": row.heater_valve/100,
        "V_valve": V_valve(row.cooling_setpoint, row.room_temp),
        "H_valve": H_valve(row.heating_setpoint, row.room_temp),
    })

print("V_error"+str(sum([abs(row["V_valve"] - row["V_valve_actual"]) for row in calculated_data])))
print("H_error"+str(sum([abs(row["H_valve"] - row["H_valve_actual"]) for row in calculated_data])))

df = pd.DataFrame(calculated_data)





def plot_df(df: pd.DataFrame) -> None:
    # Create a subplot figure with two rows
    fig = make_subplots(rows=3, cols=1, shared_xaxes=False, subplot_titles=(
        "Room Temperature and Predictions", "Heating and Solar Effects"))

    # First plot
    #fig.add_trace(go.Scatter(x=df["time"], y=df["room_temp"], mode='lines', name='Room Temp'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["H_valve_actual"][:1341], mode='lines', name='Actual Heater'), row=1,
                  col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["H_valve"][:1341], mode='lines', name='Heater'), row=1,
                  col=1)


    fig.add_trace(go.Scatter(x=df["time"], y=df["V_valve_actual"][:1341], mode='lines', name='Actual Ventilation'),
                  row=2,
                  col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["V_valve"][:1341], mode='lines', name='Ventilation'), row=2,
                  col=1)


    fig.add_trace(go.Scatter(x=df["time"], y=df["room_temp"][:1341], mode='lines', name='Room temp'),
                  row=3,
                  col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["heating_setpoint"][:1341], mode='lines', name='Heating setpoint'), row=3,
                  col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["cooling_setpoint"][:1341], mode='lines', name='Cooling setpoint'),
                  row=3,
                  col=1)





    # Update layout
    fig.update_xaxes(title_text="Time", tickangle=45, row=1, col=1)
    fig.update_yaxes(title_text="Temperature", row=1, col=1)
    fig.update_yaxes(title_text="Temperature Diff", row=2, col=1)

    fig.update_layout(title_text="Time-Series Data (Plotly)", height=1400, width=1400)

    pio.renderers.default = "browser"
    fig.show()



plot_df(df)