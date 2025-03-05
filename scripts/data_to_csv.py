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
            data_solar_watt = from(bucket:"db")
                     |> range(start: """+date_string_from+""", stop: """+date_string_to+""")
                     |> filter(fn: (r) => r["source"] == "/TM023_1_20_1103/SG01/Solar_panel_south")
                     |> filter(fn: (r) => r["_field"] == "value")
                     |> rename(columns: {_value: "solar_watt"})
        
            data_room_temp = from(bucket:"db")
                     |> range(start: """+date_string_from+""", stop: """+date_string_to+""")
                     |> filter(fn: (r) => r.room_id == "1.213") 
                     |> filter(fn: (r) => r["sensor_type"] == "temperature")
                     |> filter(fn: (r) => r["_field"] == "value")
                     |> rename(columns: {_value: "room_temp"})
                     
            data_heating_setpoint = from(bucket:"db")
                     |> range(start: """+date_string_from+""", stop: """+date_string_to+""")
                     |> filter(fn: (r) => r.room_id == "1.213") 
                     |> filter(fn: (r) => r["sensor_type"] == "setpoint")
                     |> filter(fn: (r) => r["source"] == "/TM023_3_20_1.204/Lon/Net/Rum_1.213/Temperature_heating_setpoint_1.213")
                     |> filter(fn: (r) => r["_field"] == "value") 
                     |> rename(columns: {_value: "heating_setpoint"})  
            
            data_cooling_setpoint = from(bucket:"db")
                     |> range(start: """+date_string_from+""", stop: """+date_string_to+""")
                     |> filter(fn: (r) => r.room_id == "1.213") 
                     |> filter(fn: (r) => r["sensor_type"] == "setpoint")
                     |> filter(fn: (r) => r["source"] == "/TM023_3_20_1.204/Lon/Net/Rum_1.213/Temperature_cooling_setpoint_1.213")
                     |> filter(fn: (r) => r["_field"] == "value") 
                     |> rename(columns: {_value: "cooling_setpoint"})        
                     
            solar_room = join(tables: {d1: data_solar_watt, d2: data_room_temp}, on: ["_time"])
            solar_room_heater = join(tables: {dsr: solar_room, d3: data_heating_setpoint}, on: ["_time"])
            solar_room_heater_cooler = join(tables: {dsrh: solar_room_heater, d4: data_cooling_setpoint}, on: ["_time"])
            solar_room_heater_cooler
            |> keep (columns: ["_time", "solar_watt", "room_temp", "heating_setpoint", "cooling_setpoint"])
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
                if counter < 14:
                    counter += 1
                    continue
                counter = 0
                time = record["_time"]
                outside_temp_at_given_time = None 
                for dmi_time, dmi_temp in dmi_results.items():
                    if datetime.fromisoformat(dmi_time) == hour_rounder(time):  # The time from the DMI API is rounded to the nearest hour.
                        outside_temp_at_given_time = dmi_temp
                        break
                solar_watt = record.values.get("solar_watt") 
                room_temp = round(record.values.get("room_temp"), 1) 
                heating_setpoint = record.values.get("heating_setpoint")
                cooling_setpoint = record.values.get("cooling_setpoint")

                # The data is appended to the list 'data' which is used to write to the csv file.
                data.append({"time": time,
                             "solar_watt": solar_watt,
                             "room_temp": room_temp,
                             "ambient_temp": outside_temp_at_given_time,
                             "heating_setpoint": heating_setpoint,
                             "cooling_setpoint": cooling_setpoint})

        # The data is written to the csv file.
        with open('data/data.csv', 'a', newline='') as csvfile:
            fieldnames = ['time', 'solar_watt', 'room_temp', 'ambient_temp', 'heating_setpoint', 'cooling_setpoint'] # The fieldnames for the csv file.
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
def reset_csv(path='data/data.csv'):
    with open(path, 'w', newline='') as csvfile:
        fieldnames = ['time', 'solar_watt', 'room_temp', 'ambient_temp', 'heating_setpoint', 'cooling_setpoint']  # The fieldnames for the csv file.
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  # The csv writer.
        writer.writeheader()

'''
@params alpha_a: alpha_a constant for ambient temperature
@params alpha_s: alpha_s constant for solar effect
@params alpha_r: alpha_r constant for heater effect
@params alpha_v: alpha_v constant for ventilation effect
@params start_time: start time as a string
@params days: number of days to train for
Writes the constants from the training to the cache csv file
'''
def cache_constants(alpha_a, alpha_s, alpha_r, alpha_v, start_time, days, error, path = 'data/constants_cache.csv'):
    #Open the csv file in write mode
    with open(path, 'w+', newline='') as csvfile:
        fieldnames = ['alpha_a', 'alpha_s', 'alpha_r', 'alpha_v', 'start_time', 'days', 'error'] # The fieldnames for the csv file.
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  # The csv writer.
        writer.writeheader()
        #Write the constants to the csv file
        writer.writerow({'alpha_a': alpha_a, 'alpha_s': alpha_s, 'alpha_r': alpha_r,
                          'alpha_v': alpha_v, 'start_time': start_time, 'days': days, 'error': error})

