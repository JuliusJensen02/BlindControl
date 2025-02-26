import plotly.express as px
import plotly.io as pio

def plot_df(df):
    fig = px.line(df, x=df["Watt"], y=df["C"], title="Time-Series Data (Plotly)")

    fig.update_xaxes(title="Watt", tickangle=45)
    fig.update_yaxes(title="C")
    pio.renderers.default = "browser"
    fig.show()