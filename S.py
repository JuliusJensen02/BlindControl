import plotly.express as px
import plotly.io as pio
import pandas as pd
import csv

data = {}
with open('data.csv', mode ='r') as file:
  csvFile = csv.reader(file)
  for lines in csvFile:
      c = lines[1]
      watt = lines[0]
      if c == "temp":
          continue
      if c not in data:
          data[c] = list()
      data[c].append(float(watt))




for key, record in data.items():
    watt_sum = 0
    for watt in record:
        watt_sum += watt
    watt_sum /= len(record)
    data[key] = watt_sum


sorted_data = sorted(list(data.items()), key=lambda x: x[0])

df = pd.DataFrame(list(sorted_data), columns=["Watt", "C"])

fig = px.line(df, x=df["C"], y=df["Watt"], title="Time-Series Data (Plotly)")

fig.update_xaxes(title="Watt/m2", tickangle=45)
fig.update_yaxes(title="C")
pio.renderers.default = "browser"
fig.show()