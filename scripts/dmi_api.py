import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
DMIAPIKEY = os.getenv("DMI_API_KEY")

'''
@params start: start time as a string
@params stop: stop time as a string
@returns temp_map: dict
Gets the temperatures from the DMIAPI of the given time frame in increments of 1 hour
'''
#TODO: Change from dict to DataFrame
def get_temp(start="2024-11-23T00:00:00Z", stop="2024-11-24T00:00:00Z"):
    url = 'https://dmigw.govcloud.dk/v2/climateData/collections/municipalityValue/items?municipalityId=0851&api-key='+DMIAPIKEY+'&timeResolution=hour&parameterId=mean_temp&limit=10000&datetime='+start+'/'+stop
    r = requests.get(url)
    dmi_data = json.loads(r.text)
    temp_map = {}
    for item in dmi_data.get('features'):
        temp_map[item['properties']['from']] = item['properties']['value']
    return temp_map

