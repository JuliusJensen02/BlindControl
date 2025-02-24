import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
DMIAPIKEY = os.getenv("DMIAPIKEY")

def get_temp():
    url = 'https://dmigw.govcloud.dk/v2/climateData/collections/municipalityValue/items?municipalityId=0851&api-key='+DMIAPIKEY+'&timeResolution=hour&parameterId=mean_temp'
    r = requests.get(url)
    data = json.loads(r.text)
    temp_map = {}
    for item in data.get('features'):
        temp_map[item['properties']['from']] = item['properties']['value']
    return temp_map


print(get_temp())