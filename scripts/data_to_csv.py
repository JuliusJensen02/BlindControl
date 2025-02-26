import influxdb_client
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from scripts.dmi_api import get_temp
import csv

def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
               +timedelta(hours=t.minute//30))

load_dotenv()
client = influxdb_client.InfluxDBClient(
    url=os.getenv("url"),
    token=os.getenv("token"),
    org=os.getenv("org"),
    timeout=1000_000
)

def query_data(input_from = "2024-11-23T00:00:00Z", days = 1):

    date_from = datetime.strptime(input_from, "%Y-%m-%dT%H:%M:%SZ")
    date_to = date_from + timedelta(days=1)

    for i in range(days):
        date_string_from = date_from.strftime("%Y-%m-%dT00:00:00Z")
        date_string_to = date_to.strftime("%Y-%m-%dT00:00:00Z")
        query = """
            data_1 = from(bucket:"db")
                     |> range(start: """+date_string_from+""", stop: """+date_string_to+""")
                     |> filter(fn: (r) => r["source"] == "/TM023_1_20_1103/SG01/Solar_panel_south")
                     |> filter(fn: (r) => r["_field"] == "value")
        
            data_2 = from(bucket:"db")
                     |> range(start: """+date_string_from+""", stop: """+date_string_to+""")
                     |> filter(fn: (r) => r.room_id == "1.213" or r.room_id == "1.215" or r.room_id == "1.217")
                     |> filter(fn: (r) => r["sensor_type"] == "temperature")
                     |> filter(fn: (r) => r["_field"] == "value")
        
            join(
                tables: {d1: data_1, d2: data_2},
                on: ["_time"]
            )
            """

        query_api = client.query_api()
        result = query_api.query(org=os.getenv("org"), query=query)
        dmi_results = get_temp(date_string_from, date_string_to)

        data = list()
        for table in result:
            for record in table:
                time = record["_time"]
                outside_temp_at_given_time = None
                for dmi_time, dmi_temp in dmi_results.items():
                    if datetime.fromisoformat(dmi_time) == hour_rounder(time):
                        outside_temp_at_given_time = dmi_temp
                        break
                watt = record.values.get("_value_d1")
                c = round(record.values.get("_value_d2"), 1)
                data.append({"time": time, "watt": watt, "room_temp": c, "ambient_temp": outside_temp_at_given_time})

        with open('data.csv', 'a', newline='') as csvfile:
            fieldnames = ['time', 'watt', 'room_temp', 'ambient_temp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        print("Fetched date from: "+date_string_from+", to: "+date_string_to)
        date_from += timedelta(days=1)
        date_to += timedelta(days=1)

def reset_csv():
    f = open('data.csv', 'w+')
    f.close()
