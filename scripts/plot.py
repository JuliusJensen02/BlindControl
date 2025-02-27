import plotly.express as px
import plotly.io as pio

def plot_df(df):
    fig = px.line(df, x="time", y=["room_temp", "temp_predictions"], title="Time-Series Data (Plotly)")

    fig.update_xaxes(title="Time", tickangle=45)
    fig.update_yaxes(title="Temperature")
    pio.renderers.default = "browser"
    fig.show()