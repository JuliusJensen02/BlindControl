import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
org = os.getenv("org")
token = os.getenv("token")
url = os.getenv("url")

client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)

def get_influx_data(query_string):
    query_api = client.query_api()
    result = query_api.query(org=org, query=query_string)
    results = {}
    for record in result[0].records:
        results[record.get_time().strftime("%d/%m/%Y, %H:%M:%S")] = record.get_value()
    return results

def get_room_temp(room_id, start_range="-30m"):
    query = ('from(bucket:"db")\
             |> range(start: ' + start_range + ')\
             |> filter(fn: (r) => r["room_id"] == "'+room_id+'")\
             |> filter(fn: (r) => r["sensor_type"] == "temperature")\
             |> filter(fn: (r) => r["_field"] == "value")')
    return get_influx_data(query)

def get_room_window_status(room_id, start_range="-30m"):
    query = ('from(bucket:"db")\
             |> range(start: ' + start_range + ')\
             |> filter(fn: (r) => r["room_id"] == "'+room_id+'")\
             |> filter(fn: (r) => r["sensor_type"] == "window_open")\
             |> filter(fn: (r) => r["_field"] == "value")')
    return get_influx_data(query)

def get_room_heater_status(room_id, start_range="-30m"):
    query = ('from(bucket:"db")\
             |> range(start: ' + start_range + ')\
             |> filter(fn: (r) => r["room_id"] == "'+room_id+'")\
             |> filter(fn: (r) => r["sensor_type"] == "opening_signal")\
             |> filter(fn: (r) => r["_field"] == "value")')
    return get_influx_data(query)

def get_room_occupancy_lux(room_id, start_range="-30m"):
    query = ('from(bucket:"db")\
             |> range(start: ' + start_range + ')\
             |> filter(fn: (r) => r["room_id"] == "'+room_id+'")\
             |> filter(fn: (r) => r["sensor_type"] == "occupancy")\
             |> filter(fn: (r) => r["source"] == "/TM023_3_20_1.204/Lon/Net/Rum_"'+room_id+'"/Lux_meter")\
             |> filter(fn: (r) => r["_field"] == "value")')
    return get_influx_data(query)

def get_room_occupancy_pir(room_id, start_range="-30m"):
    query = ('from(bucket:"db")\
             |> range(start: ' + start_range + ')\
             |> filter(fn: (r) => r["room_id"] == "'+room_id+'")\
             |> filter(fn: (r) => r["sensor_type"] == "occupancy")\
             |> filter(fn: (r) => r["source"] == "/TM023_3_20_1.204/Lon/Net/Rum_"'+room_id+'"/PIR_activity_"'+room_id+'"")\
             |> filter(fn: (r) => r["_field"] == "value")')
    return get_influx_data(query)

def get_room_co2(room_id, start_range="-30m"):
    query = ('from(bucket:"db")\
             |> range(start: ' + start_range + ')\
             |> filter(fn: (r) => r["room_id"] == "'+room_id+'")\
             |> filter(fn: (r) => r["sensor_type"] == "co2")\
             |> filter(fn: (r) => r["_field"] == "value")')
    return get_influx_data(query)

def get_south_facade_sun(start_range="-30m"):
    query = ('from(bucket:"db")\
             |> range(start: ' + start_range + ')\
             |> filter(fn: (r) => r["room_id"] == "tmv23")\
             |> filter(fn: (r) => r["source"] == "/TM023_1_20_1103/SG01/Solar_panel_south ")\
             |> filter(fn: (r) => r["_field"] == "value")')
    return get_influx_data(query)

print(get_room_temp("1.233"))
print(get_room_co2("1.233"))