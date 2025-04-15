import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from pandas.core.interchange.dataframe_protocol import DataFrame
from plotly.subplots import make_subplots

"""
Function used to plot the predicted temperatures from Python and UPPAAL alongside the 
heating- and cooling setpoints.
Args:
    df: Dataframe.
"""
def plot_df(df: pd.DataFrame) -> None:
    # Create a subplot figure with two rows
    fig = make_subplots(rows=2, cols=1, shared_xaxes=False, subplot_titles=(
        "Room Temperature and Predictions", "Heating and Solar Effects"))

    # First plot
    #fig.add_trace(go.Scatter(x=df["time"], y=df["room_temp"], mode='lines', name='Room Temp'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["temp_predictions"][:1341], mode='lines', name='Temp Predictions'), row=1,
                  col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["temp_predictions_uppaal"][:1341], mode='lines', name='UPPAAL'), row=1,
                  col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["room_temp"][:1341], mode='lines', name='Room temp'), row=1,
                  col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["heating_setpoint"][:1341], mode='lines', name='Heating Setpoint'), row=1,
                  col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["cooling_setpoint"][:1341], mode='lines', name='Cooling Setpoint'), row=1,
                  col=1)

    fig.add_trace(go.Scatter(x=df["time"], y=df["temp_predictions_uppaal"][:1341]-df["heating_setpoint"][:1341], mode='lines', name='UPPAAL'), row=2,
                  col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["temp_predictions"][:1341] - df["heating_setpoint"][:1341], mode='lines', name='Temp Predictions'), row=2,
                  col=1)

    print("Uppaal: "+str(np.mean(df["temp_predictions_uppaal"][:1341]-df["heating_setpoint"][:1341])))
    print("Temp Predictions: " + str(np.mean(df["temp_predictions"][:1341] - df["heating_setpoint"][:1341])))

    # Update layout
    fig.update_xaxes(title_text="Time", tickangle=45, row=1, col=1)
    fig.update_yaxes(title_text="Temperature", row=1, col=1)
    fig.update_yaxes(title_text="Temperature Diff", row=2, col=1)

    fig.update_layout(title_text="Time-Series Data (Plotly)", height=800, width=1400)

    pio.renderers.default = "browser"
    fig.show()