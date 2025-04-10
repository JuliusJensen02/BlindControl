import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

'''
@params df: DataFrame
Plots a DataFrame with the time on x-axis and two different sets of y-axis variables in subplots
'''
def plot_df(df):
    # Create a subplot figure with two rows
    fig = make_subplots(rows=1, cols=1, shared_xaxes=False, subplot_titles=(
        "Room Temperature and Predictions", "Heating and Solar Effects"))

    # First plot
    #fig.add_trace(go.Scatter(x=df["time"], y=df["room_temp"], mode='lines', name='Room Temp'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["temp_predictions"], mode='lines', name='Temp Predictions'), row=1,
                  col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["temp_predictions_uppaal"], mode='lines', name='UPPAAL'), row=1,
                  col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["heating_setpoint"], mode='lines', name='Heating Setpoint'), row=1,
                  col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["cooling_setpoint"], mode='lines', name='Cooling Setpoint'), row=1,
                  col=1)

    # Update layout
    fig.update_xaxes(title_text="Time", tickangle=45, row=1, col=1)
    fig.update_yaxes(title_text="Temperature", row=1, col=1)

    fig.update_layout(title_text="Time-Series Data (Plotly)", height=800, width=1400)

    pio.renderers.default = "browser"
    fig.show()