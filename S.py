import plotly.express as px
import plotly.io as pio
import pandas as pd
import csv


data = {}
with open('data.csv', mode ='r') as file:
  csvFile = csv.reader(file)
  for lines in csvFile:
      c = lines[1]
      if c == "temp":
          continue
      c = float(c)
      watt = float(lines[0])
      if c > 21:
        if c not in data:
          data[c] = list()
        data[c].append(watt)

for key in list(data.keys()):
    filtered = remove_outliers(data[key])
    if len(filtered) > 0:
        data.pop(key)
        continue
    watt_sum = 0
    for watt in data[key]:
        watt_sum += watt
    watt_sum /= len(data[key])
    data[key] = watt_sum


sorted_data = sorted(list(data.items()), key=lambda x: x[0])

df = pd.DataFrame(list(sorted_data), columns=["C", "Watt"])

fig = px.line(df, x=df["Watt"], y=df["C"], title="Time-Series Data (Plotly)")

fig.update_xaxes(title="Watt", tickangle=45)
fig.update_yaxes(title="C")
pio.renderers.default = "browser"
fig.show()