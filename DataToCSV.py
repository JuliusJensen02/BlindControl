import influxdb_client
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
client = influxdb_client.InfluxDBClient(
    url=os.getenv("url"),
    token=os.getenv("token"),
    org=os.getenv("org"),
    timeout=1000_000
)

date_from = datetime.strptime("2024-11-23T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
date_to = datetime.strptime("2024-11-24T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")

for i in range(90):
    date_string_from = date_from.strftime("%Y-%m-%dT00:00:00Z")
    date_string_to = date_to.strftime("%Y-%m-%dT00:00:00Z")
    query = """
        data_1 = from(bucket:"db")
                 |> range(start: """+date_string_from+""", stop: """+date_string_to+""")
                 |> filter(fn: (r) => r["source"] == "/TM023_1_20_1103/SG01/Solar_panel_south")
                 |> filter(fn: (r) => r["_field"] == "value")
    
        data_2 = from(bucket:"db")
                 |> range(start: """+date_string_from+""", stop: """+date_string_to+""")
                 |> filter(fn: (r) => r["room_id"] == "1.233")
                 |> filter(fn: (r) => r["sensor_type"] == "temperature")
                 |> filter(fn: (r) => r["_field"] == "value")
    
        join(
            tables: {d1: data_1, d2: data_2},
            on: ["_time"]
        )
        """

    query_api = client.query_api()
    result = query_api.query(org=os.getenv("org"), query=query)
    data = list()
    for record in result[0]:
        watt = record.values.get("_value_d1")
        c = round(record.values.get("_value_d2")*2)/2
        data.append({"watt": watt, "temp": c})


    import csv
    with open('data.csv', 'a', newline='') as csvfile:
        fieldnames = ['watt', 'temp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print("Fetched date from: "+date_string_from+", to: "+date_string_to)
    date_from += timedelta(days=1)
    date_to += timedelta(days=1)
