import multiprocessing
import influxdb_client
import os

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta

from influxdb_client.client.flux_table import FluxTable

from scripts.dmi_api import get_temp

"""
This function rounds the given datetime to the nearest hour.
If the minute is greater than or equal to 30, the hour is incremented by 1.
Args:
    t: datetime
Returns:
    A datetime rounded to the nearest hour.
"""
def hour_rounder(t: datetime) -> datetime:
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
            + timedelta(hours=t.minute // 30))


"""
Environment variables are loaded from the .env file.
And used to access the InfluxDB.
"""
load_dotenv()
client = influxdb_client.InfluxDBClient(
    url=os.getenv("INFLUXDB_URL"),
    token=os.getenv("INFLUXDB_TOKEN"),
    org=os.getenv("INFLUXDB_ORG"),
    timeout=1000_000
)

"""
This function queries the data from the InfluxDB and writes it to a csv file.
The data is queried for the given number of days starting from the given date.
The data is filtered based on the source and the room_id.
The data is joined based on the time.
The data is fetched from the DMI API for the given date.
The data is written to the csv file.
Args:
    room: Dict Containing all information about the room.
    from_date: Start date of query.
    day: Int portraying which date the data is being collected from.
@return None
"""
def query_data(room: dict, from_date: str, day: int) -> None:
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
                 |> keep(columns: ["_time", "_value"])
                 |> rename(columns: {_value: "solar_watt"})

        data_room_temp = from(bucket:"db")
                 |> range(start: """ + date_string_from + """, stop: """ + date_string_to + """)
                 |> filter(fn: (r) => r.room_id == \"""" + room["name"] + """\") 
                 |> filter(fn: (r) => r["sensor_type"] == "temperature")
                 |> filter(fn: (r) => r["_field"] == "value")
                 |> keep(columns: ["_time", "_value"])
                 |> rename(columns: {_value: "room_temp"})

        data_heating_setpoint = from(bucket:"db")
                 |> range(start: """ + date_string_from + """, stop: """ + date_string_to + """)
                 |> filter(fn: (r) => r.room_id == \"""" + room["name"] + """\") 
                 |> filter(fn: (r) => r["sensor_type"] == "setpoint")
                 |> filter(fn: (r) => r["source"] == "/TM023_3_20_1.204/Lon/Net/Rum_""" + room["name"] + """/Temperature_heating_setpoint_""" + room["name"] + """")
                 |> filter(fn: (r) => r["_field"] == "value") 
                 |> keep(columns: ["_time", "_value"])
                 |> rename(columns: {_value: "heating_setpoint"})  

        data_cooling_setpoint = from(bucket:"db")
                 |> range(start: """ + date_string_from + """, stop: """ + date_string_to + """)
                 |> filter(fn: (r) => r.room_id == \"""" + room["name"] + """\") 
                 |> filter(fn: (r) => r["sensor_type"] == "setpoint")
                 |> filter(fn: (r) => r["source"] == "/TM023_3_20_1.204/Lon/Net/Rum_""" + room["name"] + """/Temperature_cooling_setpoint_""" + room["name"] + """")
                 |> filter(fn: (r) => r["_field"] == "value") 
                 |> keep(columns: ["_time", "_value"])
                 |> rename(columns: {_value: "cooling_setpoint"}) 

        data_lux = from(bucket:"db")
                 |> range(start: """ + date_string_from + """, stop: """ + date_string_to + """)
                 |> filter(fn: (r) => r.room_id == \"""" + room["name"] + """\") 
                 |> filter(fn: (r) => r["sensor_type"] == "occupancy")
                 |> filter(fn: (r) => r["source"] == "/TM023_3_20_1.204/Lon/Net/Rum_""" + room["name"] + """/Lux""" + room["source_lux"] + """\")
                 |> filter(fn: (r) => r["_field"] == "value") 
                 |> keep(columns: ["_time", "_value"])
                 |> rename(columns: {_value: "lux"})
                 
        data_wind = from(bucket:"db")
                 |> range(start: """ + date_string_from + """, stop: """ + date_string_to + """)
                 |> filter(fn: (r) => r["source"] == "/TM023_1_20_1103/SG01/Wind_velocity")
                 |> filter(fn: (r) => r["_field"] == "value")
                 |> keep(columns: ["_time", "_value"])
                 |> rename(columns: {_value: "wind"})
        
        data_supply_damper = from(bucket:"db")
                 |> range(start: """ + date_string_from + """, stop: """ + date_string_to + """)
                 |> filter(fn: (r) => r.room_id == \"""" + room["name"] + """\") 
                 |> filter(fn: (r) => r["sensor_type"] == "supply_damper")
                 |> filter(fn: (r) => r["_field"] == "value")
                 |> keep(columns: ["_time", "_value"])
                 |> rename(columns: {_value: "ventilation_supply_damper"})
                 
        data_heater_valve = from(bucket:"db")
                 |> range(start: """ + date_string_from + """, stop: """ + date_string_to + """)
                 |> filter(fn: (r) => r.room_id == \"""" + room["name"] + """\") 
                 |> filter(fn: (r) => r["sensor_type"] == "opening_signal")
                 |> filter(fn: (r) => r["_field"] == "value")
                 |> keep(columns: ["_time", "_value"])
                 |> rename(columns: {_value: "heater_valve"})
    

        solar_room = join(tables: {d1: data_solar_watt, d2: data_room_temp}, on: ["_time"])
        solar_room_heater = join(tables: {d1: solar_room, d2: data_heating_setpoint}, on: ["_time"])
        solar_room_heater_cooler = join(tables: {d1: solar_room_heater, d2: data_cooling_setpoint}, on: ["_time"])
        solar_room_heater_cooler_lux = join(tables: {d1: solar_room_heater_cooler, d2: data_lux}, on: ["_time"])
        solar_room_heater_cooler_lux_wind = join(tables: {d1: solar_room_heater_cooler_lux, d2: data_wind}, on: ["_time"])
        solar_room_heater_cooler_lux_wind_heatervalve = join(tables: {d1: solar_room_heater_cooler_lux_wind, d2: data_heater_valve}, on: ["_time"])
        
        solar_room_heater_cooler_lux_wind_heatervalve
        |> keep (columns: ["_time", "solar_watt", "room_temp", "heating_setpoint", "cooling_setpoint", "lux", "wind", "heater_valve"])
        """

    query2 = """
            data_supply_damper = from(bucket:"db")
                     |> range(start: """ + date_string_from + """, stop: """ + date_string_to + """)
                     |> filter(fn: (r) => r.room_id == \"""" + room["name"] + """\") 
                     |> filter(fn: (r) => r["sensor_type"] == "supply_damper")
                     |> filter(fn: (r) => r["_field"] == "value")
                     |> keep(columns: ["_time", "_value"])
                     |> rename(columns: {_value: "ventilation_supply_damper"})
                     |> truncateTimeColumn(unit: 1m)
                     
            data_supply_damper
            |> keep (columns: ["_time", "ventilation_supply_damper"])
            """
    # The query_api is used to query the data from the InfluxDB.
    # The result is stored in the variable 'result'.
    query_api = client.query_api()
    result = query_api.query(org=os.getenv("org"), query=query)
    ventilation_supply_damper_result = query_api.query(org=os.getenv("org"), query=query2)
    dmi_results = get_temp(date_string_from, date_string_to)

    ventilation_supply_damper_df = get_ventilation_supply_damper(ventilation_supply_damper_result[0], result[0])
    df = merge_dmi_data(result[0], dmi_results)

    df = pd.merge(df, ventilation_supply_damper_df, on="time", how="left")

    df.to_csv('data/'""+ room["name"] +""'/query_data/data_' + date_from.strftime("%Y-%m-%d") + '.csv', mode='w')

    # Confirmation message
    print("Fetched data from: " + date_string_from + ", to: " + date_string_to)

"""
Collects the data using multiprocessing.
Args:
    from_date: Start date of query collection.
    to_date: End date of query collection.
    room: Dict containing all information about the room.
"""
def query_data_period(from_date: str, to_date:str, room: dict) -> None:
    current_date = datetime.strptime(from_date, "%Y-%m-%dT%H:%M:%SZ")
    days = (datetime.strptime(to_date, "%Y-%m-%dT%H:%M:%SZ") - current_date).days
    with multiprocessing.Pool(processes=5) as pool:
        # Map the days to the pool workers
        pool.starmap(query_data, [(room, from_date, i) for i in range(days)])


def interpolate_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Interpolates the missing data in the dataframe.
    Args:
        df: Dataframe to interpolate.
    Returns:
        Dataframe with interpolated data.
    """
    # Interpolate the missing data
    df = df.interpolate(method='linear', limit_direction='both')
    # Fill any remaining NaN values with the mean of the column
    df.fillna(df.mean(), inplace=True)
    return df

def get_ventilation_supply_damper(ventilation_table: FluxTable, reference_table: FluxTable) -> pd.DataFrame:
    buffer = list()

    for record in reference_table:
        time = record.values.get("_time")
        damper_value = None
        for record2 in ventilation_table:
            time2 = record2.values.get("_time")
            value = record2.values.get("ventilation_supply_damper")

            if time == time2:
                damper_value = value
                break

        buffer.append({"time": time,
                       "ventilation_supply_damper": damper_value})
    return interpolate_data(pd.DataFrame(buffer))


def merge_dmi_data(result: FluxTable, dmi_df: pd.DataFrame) -> pd.DataFrame:
    # The data is written to the csv file.
    # The data is fetched from the result and the DMI API and joined based on the time before writing to the csv file.
    data = list()
    for record in result:
        time = record["_time"]
        outside_temp_at_given_time = None
        for dmi_time, dmi_temp in dmi_df.values:
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
        heater_valve = record.values.get("heater_valve")

        # The data is appended to the list 'data' which is used to write to the csv file.
        data.append({"time": time,
                     "solar_watt": solar_watt,
                     "room_temp": room_temp,
                     "ambient_temp": outside_temp_at_given_time,
                     "heating_setpoint": heating_setpoint,
                     "cooling_setpoint": cooling_setpoint,
                     "lux": lux,
                     "wind": wind,
                     "heater_valve": heater_valve})

    return pd.DataFrame(data)