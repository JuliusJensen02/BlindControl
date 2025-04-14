import requests
import json
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
DMIAPIKEY = os.getenv("DMI_API_KEY")

"""
Gets the temperatures from the DMIAPI of the given time frame in increments of 1 hour.
Args:
    start: start time as a string.
    stop: stop time as a string.
Returns:
    temp_map: dict
"""

def get_temp(start: str="2024-11-23T00:00:00Z", stop: str="2024-11-24T00:00:00Z"):
    url = 'https://dmigw.govcloud.dk/v2/climateData/collections/municipalityValue/items?municipalityId=0851&api-key='+DMIAPIKEY+'&timeResolution=hour&parameterId=mean_temp&limit=10000&datetime='+start+'/'+stop
    r = requests.get(url)
    dmi_data = json.loads(r.text)
    #temp_map = {}
    times = []
    temperatures = []

    for item in dmi_data.get('features'):
        #temp_map[item['properties']['from']] = item['properties']['value']
        times.append(item['properties']['from'])
        temperatures.append(item['properties']['value'])
    # Create a DataFrame from the lists
    df = pd.DataFrame({
        'datetime': times,
        'mean_temp': temperatures
    })

    # Convert the 'datetime' column to datetime type (if needed for further manipulation)
    df['datetime'] = pd.to_datetime(df['datetime'])

    return df


