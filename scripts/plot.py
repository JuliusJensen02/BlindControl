import plotly.express as px
import plotly.io as pio

from scripts.data_processing import normalize

'''
@params df: DataFrame
Plots a DataFrame with the time on x-axis, and room_temp and temp_predictions on y-axis
'''
def plot_df(df):
    #Lines are drawn with time as the x-axis and room_temp and temp_predictions as the y-axis
    fig = px.line(df, x="time", y=["room_temp", "temp_predictions", "heating_setpoint", "cooling_setpoint"], title="Time-Series Data (Plotly)")

    fig.update_xaxes(title="Time", tickangle=45)
    fig.update_yaxes(title="Temperature")
    pio.renderers.default = "browser"
    fig.show()