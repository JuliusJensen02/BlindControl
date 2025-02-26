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
    for table in result:
        for record in table.records:
            results[record.get_time().strftime("%d/%m/%Y, %H:%M")] = record.get_value()
    return results

def get_room_temp(room_id, start_range="-30m"):
    query = ('from(bucket:"db")\
             |> range(start: 2025-02-23T00:00:00Z, stop: 2025-02-24T00:00:00Z)\
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
             |> range(start: 2025-02-23T00:00:00Z, stop: 2025-02-24T00:00:00Z)\
             |> filter(fn: (r) => r["source"] == "/TM023_1_20_1103/SG01/Solar_panel_south")\
             |> filter(fn: (r) => r["_field"] == "value")')
    return get_influx_data(query)

#print(get_south_facade_sun())
#print(get_room_temp("1.233"))

import matplotlib.pyplot as plt
import numpy as np
import math


data1 = get_south_facade_sun()
data2 = get_room_temp("1.233")

x = list(data1.keys())


# Assign variables to the y axis part of the curve
y = normalize(remove_outliers(list(data1.values())))
z = normalize(remove_outliers(list(data2.values())))
print(len(y), len(z))

for i in range(1,12):
    x.pop()
    y.pop()

# Plotting both the curves simultaneously
plt.plot(x, y, color='r', label='Watt/m2')
plt.plot(x, z, color='g', label='Celsius')

# Naming the x-axis, y-axis and the whole graph
plt.xlabel("Time")
plt.ylabel("Values")
plt.title("Sun and Temperature")

# Adding legend, which helps us recognize the curve according to it's color
plt.legend()

# To load the display window
plt.show()
