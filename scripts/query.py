import multiprocessing
import influxdb_client
import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
from scripts.dmi_api import get_temp

'''
@param t: datetime
@return t: datetime
This function rounds the given datetime to the nearest hour.
If the minute is greater than or equal to 30, the hour is incremented by 1.
'''
def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
            + timedelta(hours=t.minute // 30))


'''
Environment variables are loaded from the .env file.
And used to access the InfluxDB.
'''
load_dotenv()
client = influxdb_client.InfluxDBClient(
    url=os.getenv("INFLUXDB_URL"),
    token=os.getenv("INFLUXDB_TOKEN"),
    org=os.getenv("INFLUXDB_ORG"),
    timeout=1000_000
)

"""
@param input_from: str
@param days: int
@return None
This function queries the data from the InfluxDB and writes it to a csv file.
The data is queried for the given number of days starting from the given date.
The data is filtered based on the source and the room_id.
The data is joined based on the time.
The data is fetched from the DMI API for the given date.
The data is written to the csv file.
"""
def query_data(room, from_date, day):
    from_date = datetime.strptime(from_date, "%Y-%m-%dT%H:%M:%SZ")
    date_from = from_date + timedelta(days=day)
    # The input_from is converted to a datetime object of the format "%Y-%m-%dT%H:%M:%SZ".

    # The date_to is calculated by adding the number of days to the date_from.
    date_to = date_from + timedelta(days=1)

    # The dates are converted to strings of the format "%Y-%m-%dT00:00:00Z".
    date_string_from = date_from.strftime("%Y-%m-%dT00:00:00Z")
    date_string_to = date_to.strftime("%Y-%m-%dT00:00:00Z")

    # The query to fetch the data from the InfluxDB written in the InfluxDB Flux language.
    # The data is filtered based on the source and the room_id. Add 'or r.room_id == "1.215" or r.room_id == "1.217"' to filter for other rooms.
    query = """
        data_solar_watt = from(bucket:"db")
                 |> range(start: """ + date_string_from + """, stop: """ + date_string_to + """)
                 |> filter(fn: (r) => r["source"] == "/TM023_1_20_1103/SG01/Solar_panel_south")
                 |> filter(fn: (r) => r["_field"] == "value")
                 |> rename(columns: {_value: "solar_watt"})

        data_room_temp = from(bucket:"db")
                 |> range(start: """ + date_string_from + """, stop: """ + date_string_to + """)
                 |> filter(fn: (r) => r.room_id == \"""" + room["name"] + """\") 
                 |> filter(fn: (r) => r["sensor_type"] == "temperature")
                 |> filter(fn: (r) => r["_field"] == "value")
                 |> rename(columns: {_value: "room_temp"})

        data_heating_setpoint = from(bucket:"db")
                 |> range(start: """ + date_string_from + """, stop: """ + date_string_to + """)
                 |> filter(fn: (r) => r.room_id == \"""" + room["name"] + """\") 
                 |> filter(fn: (r) => r["sensor_type"] == "setpoint")
                 |> filter(fn: (r) => r["source"] == "/TM023_3_20_1.204/Lon/Net/Rum_""" + room["name"] + """/Temperature_heating_setpoint_""" + room["name"] + """")
                 |> filter(fn: (r) => r["_field"] == "value") 
                 |> rename(columns: {_value: "heating_setpoint"})  

        data_cooling_setpoint = from(bucket:"db")
                 |> range(start: """ + date_string_from + """, stop: """ + date_string_to + """)
                 |> filter(fn: (r) => r.room_id == \"""" + room["name"] + """\") 
                 |> filter(fn: (r) => r["sensor_type"] == "setpoint")
                 |> filter(fn: (r) => r["source"] == "/TM023_3_20_1.204/Lon/Net/Rum_""" + room["name"] + """/Temperature_cooling_setpoint_""" + room["name"] + """")
                 |> filter(fn: (r) => r["_field"] == "value") 
                 |> rename(columns: {_value: "cooling_setpoint"}) 

        data_lux = from(bucket:"db")
                 |> range(start: """ + date_string_from + """, stop: """ + date_string_to + """)
                 |> filter(fn: (r) => r.room_id == \"""" + room["name"] + """\") 
                 |> filter(fn: (r) => r["sensor_type"] == "occupancy")
                 |> filter(fn: (r) => r["source"] == "/TM023_3_20_1.204/Lon/Net/Rum_""" + room["name"] + """/Lux""" + room["source_lux"] + """\")
                 |> filter(fn: (r) => r["_field"] == "value") 
                 |> rename(columns: {_value: "lux"})
                 
        data_wind = from(bucket:"db")
                 |> range(start: """ + date_string_from + """, stop: """ + date_string_to + """)
                 |> filter(fn: (r) => r["source"] == "/TM023_1_20_1103/SG01/Wind_velocity")
                 |> filter(fn: (r) => r["_field"] == "value")
                 |> rename(columns: {_value: "wind"})
    

        solar_room = join(tables: {d1: data_solar_watt, d2: data_room_temp}, on: ["_time"])
        solar_room_heater = join(tables: {dsr: solar_room, d3: data_heating_setpoint}, on: ["_time"])
        solar_room_heater_cooler = join(tables: {dsrh: solar_room_heater, d4: data_cooling_setpoint}, on: ["_time"])
        solar_room_heater_cooler_lux = join(tables: {dsrhc: solar_room_heater_cooler, d5: data_lux}, on: ["_time"])
        solar_room_heater_cooler_lux_wind = join(tables: {dsrhc: solar_room_heater_cooler_lux, d5: data_wind}, on: ["_time"])
        solar_room_heater_cooler_lux_wind
        |> keep (columns: ["_time", "solar_watt", "room_temp", "heating_setpoint", "cooling_setpoint", "lux", "wind"])
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
    for table in result:
        for record in table:
            time = record["_time"]
            outside_temp_at_given_time = None
            for dmi_time, dmi_temp in dmi_results.values:
                if dmi_time == "datetime" or dmi_temp == "mean_temp": continue
                if datetime.strftime(dmi_time, "%Y-%m-%d %H:%M:%S%z") == datetime.strftime(hour_rounder(time), "%Y-%m-%d %H:%M:%S%z"):  # The time from the DMI API is rounded to the nearest hour.
                    outside_temp_at_given_time = dmi_temp
                    break
            solar_watt = record.values.get("solar_watt")
            room_temp = round(record.values.get("room_temp"), 1)
            heating_setpoint = record.values.get("heating_setpoint")
            cooling_setpoint = record.values.get("cooling_setpoint")
            lux = record.values.get("lux")
            wind = record.values.get("wind")

            # The data is appended to the list 'data' which is used to write to the csv file.
            data.append({"time": time,
                         "solar_watt": solar_watt,
                         "room_temp": room_temp,
                         "ambient_temp": outside_temp_at_given_time,
                         "heating_setpoint": heating_setpoint,
                         "cooling_setpoint": cooling_setpoint,
                         "lux": lux,
                         "wind": wind})

    df = pd.DataFrame(data)
    # df = remove_outliers(df)  # Remove outliers from the dataframe
    #df = smooth(df, 'room_temp')  # Smooth the dataframe

    df.to_csv('data/'""+ room["name"] +""'/query_data/data_' + date_from.strftime("%Y-%m-%d") + '.csv', mode='w')

    # Confirmation message
    print("Fetched data from: " + date_string_from + ", to: " + date_string_to)


def query_data_period(from_date, to_date, room):
    current_date = datetime.strptime(from_date, "%Y-%m-%dT%H:%M:%SZ")
    days = (datetime.strptime(to_date, "%Y-%m-%dT%H:%M:%SZ") - current_date).days
    with multiprocessing.Pool(processes=5) as pool:
        # Map the days to the pool workers
        pool.starmap(query_data, [(room, from_date, i) for i in range(days)])