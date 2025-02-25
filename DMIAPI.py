import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
DMIAPIKEY = os.getenv("DMIAPIKEY")

def get_temp():
    url = 'https://dmigw.govcloud.dk/v2/climateData/collections/municipalityValue/items?municipalityId=0851&api-key='+DMIAPIKEY+'&timeResolution=hour&parameterId=mean_temp&limit=1000'
    r = requests.get(url)
    data = json.loads(r.text)
    temp_map = {}
    for item in data.get('features'):
        temp_map[item['properties']['from']] = item['properties']['value']
    return temp_map


#print(get_temp())

import plotly.express as px
import pandas as pd

data = get_temp()

df = pd.DataFrame(list(data.items()), columns=["Time", "Value"])

# Create an interactive plot
fig = px.line(df, x="Time", y="Value", title="Time-Series Data (Plotly)")


fig.update_xaxes(title="Time", tickformat="%m-%d %H:%M", tickangle=45, dtick="D1")
fig.update_yaxes(title="Value")

fig.show()