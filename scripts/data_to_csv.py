import influxdb_client
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from scripts.dmi_api import get_temp
import csv

'''
@param t: datetime
@return t: datetime
This function rounds the given datetime to the nearest hour.
If the minute is greater than or equal to 30, the hour is incremented by 1.
'''
def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
               +timedelta(hours=t.minute//30))

'''
Environment variables are loaded from the .env file.
And used to access the InfluxDB.
'''
load_dotenv()
client = influxdb_client.InfluxDBClient(
    url=os.getenv("url"),
    token=os.getenv("token"),
    org=os.getenv("org"),
    timeout=1000_000
)

'''
@param input_from: str
@param days: int
@return None
This function queries the data from the InfluxDB and writes it to a csv file.
The data is queried for the given number of days starting from the given date.
The data is filtered based on the source and the room_id.
The data is joined based on the time.
The data is fetched from the DMI API for the given date.
The data is written to the csv file.
'''
def query_data(input_from = "2024-11-25T00:00:00Z", days = 1):

    # The input_from is converted to a datetime object of the format "%Y-%m-%dT%H:%M:%SZ".
    date_from = datetime.strptime(input_from, "%Y-%m-%dT%H:%M:%SZ")

    # The date_to is calculated by adding the number of days to the date_from.
    date_to = date_from + timedelta(days=1)

    for i in range(days):
        # The dates are converted to strings of the format "%Y-%m-%dT00:00:00Z".
        date_string_from = date_from.strftime("%Y-%m-%dT00:00:00Z")
        date_string_to = date_to.strftime("%Y-%m-%dT00:00:00Z")
        
        # The query to fetch the data from the InfluxDB written in the InfluxDB Flux language.
        # The data is filtered based on the source and the room_id. Add 'or r.room_id == "1.215" or r.room_id == "1.217"' to filter for other rooms.
        query = """
            data_1 = from(bucket:"db")
                     |> range(start: """+date_string_from+""", stop: """+date_string_to+""")
                     |> filter(fn: (r) => r["source"] == "/TM023_1_20_1103/SG01/Solar_panel_south")
                     |> filter(fn: (r) => r["_field"] == "value")
                     |> rename(columns: {_value: "watt"})
        
            data_2 = from(bucket:"db")
                     |> range(start: """+date_string_from+""", stop: """+date_string_to+""")
                     |> filter(fn: (r) => r.room_id == "1.213") 
                     |> filter(fn: (r) => r["sensor_type"] == "temperature")
                     |> filter(fn: (r) => r["_field"] == "value")
                     |> rename(columns: {_value: "room_temp"})
                     
            data_3 = from(bucket:"db")
                     |> range(start: """+date_string_from+""", stop: """+date_string_to+""")
                     |> filter(fn: (r) => r.room_id == "1.213") 
                     |> filter(fn: (r) => r["sensor_type"] == "opening_signal")
                     |> filter(fn: (r) => r["_field"] == "value")
                     |> rename(columns: {_value: "opening_signal"})
            
            data_4 = from(bucket:"db")
                     |> range(start: """+date_string_from+""", stop: """+date_string_to+""")
                     |> filter(fn: (r) => r["source"] == "/TM023_0_21_1101/Lon/Net/VA01-QMV01/Kamstrup_HEAT_KMP_TAC/Node_Object_[0]/Supply_temperature_north_east_VA01")
                     |> filter(fn: (r) => r["_field"] == "value") 
                     |> rename(columns: {_value: "supply_temp"})
             
            data_5 = from(bucket:"db")
                     |> range(start: """+date_string_from+""", stop: """+date_string_to+""")
                     |> filter(fn: (r) => r.room_id == "1.213") 
                     |> filter(fn: (r) => r["sensor_type"] == "setpoint")
                     |> filter(fn: (r) => r["source"] == "/TM023_3_20_1.204/Lon/Net/Rum_1.213/Temperature_heating_setpoint_1.213")
                     |> filter(fn: (r) => r["_field"] == "value") 
                     |> rename(columns: {_value: "heating_setpoint"})        
                     
            watt_temp = join(tables: {d1: data_1, d2: data_2}, on: ["_time"])
            watt_temp_rad = join(tables: {dwt: watt_temp, d3: data_3}, on: ["_time"])
            watt_temp_rad_supply = join(tables: {dwts: watt_temp_rad, d4: data_4}, on: ["_time"])
            watt_temp_rad_supply_setpoint = join(tables: {dwts: watt_temp_rad_supply, d5: data_5}, on: ["_time"])
            watt_temp_rad_supply_setpoint
            |> keep (columns: ["_time", "watt", "room_temp", "opening_signal", "supply_temp", "heating_setpoint"])
            """ 

        # The query_api is used to query the data from the InfluxDB.
        # The result is stored in the variable 'result'.
        query_api = client.query_api()
        result = query_api.query(org=os.getenv("org"), query=query)

        # The data is fetched from the DMI API for the given date.
        dmi_results = get_temp(date_string_from, date_string_to)

        # The data is written to the csv file.
        # The data is fetched from the result and the DMI API and joined based on the time before writing to the csv file.
        data = list()
        counter = 0
        for table in result:
            for record in table:
                if counter < 15:
                    counter += 1
                    continue
                counter = 0
                time = record["_time"]
                outside_temp_at_given_time = None 
                for dmi_time, dmi_temp in dmi_results.items():
                    if datetime.fromisoformat(dmi_time) == hour_rounder(time):  # The time from the DMI API is rounded to the nearest hour.
                        outside_temp_at_given_time = dmi_temp
                        break
                watt = record.values.get("watt") # The value of the column 'value' from the table 'data_1'.
                room_temp = round(record.values.get("room_temp"), 1) # The value of the column 'value' from the table 'data_2'.
                heating_setpoint = record.values.get("heating_setpoint")
                supply_temp = record.values.get("supply_temp")
                opening_signal = record.values.get("opening_signal")

                # The data is appended to the list 'data'.
                data.append({"time": time,
                             "watt": watt,
                             "room_temp": room_temp,
                             "ambient_temp": outside_temp_at_given_time,
                             "opening_signal": opening_signal})

        # The data is written to the csv file.
        with open('data/data.csv', 'a', newline='') as csvfile:
            fieldnames = ['time', 'watt', 'room_temp', 'ambient_temp', 'opening_signal'] # The fieldnames for the csv file.
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames) # The csv writer.
            writer.writerows(data)

        # Confirmation message
        print("Fetched date from: "+date_string_from+", to: "+date_string_to)

        # The date_from and date_to are incremented by 1 day.
        date_from += timedelta(days=1)
        date_to += timedelta(days=1)

'''
The data in the csv file is reset.
'''
def reset_csv():
    f = open('data/data.csv', 'w+')
    f.close()
    with open('data/data.csv', 'a', newline='') as csvfile:
        fieldnames = ['time', 'watt', 'room_temp', 'ambient_temp', 'opening_signal']  # The fieldnames for the csv file.
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  # The csv writer.
        writer.writeheader()