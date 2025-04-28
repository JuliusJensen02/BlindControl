from datetime import datetime, timedelta
import pandas as pd
import torch
import numpy as np


"""
This function converts the csv data into a DataFrame.
Args:
    from_date: Date of the data.
    room: Dict containing information regarding the room that the data is converted from.
    processed_data: Boolean that indicates if the data is processed or not.
Returns
    df: DataFrame
"""
def convert_csv_to_df(from_date: datetime, room: dict, processed_data = False) -> pd.DataFrame:
    # Read the csv data into a DataFrame:
    # The csv-data is the path to the csv file containing the data.
    data_path = "query_data"
    if processed_data:
        data_path = "processed_data"
    df = pd.read_csv('data/'"" + room["name"] + ""'/' + data_path + '/data_' + from_date.strftime("%Y-%m-%d") + '.csv')
    df = df.sort_values(by="time")
    return df

"""
Function that converts the processed data to a csv.
    Args:
        from_date: Date of the data.
        room: Dict containing information regarding the room that the data is converted from.
    Returns:
        A dataframe containing the processed data.
"""
def get_processed_data_as_df(from_date: datetime, room: dict) -> pd.DataFrame:
    return convert_csv_to_df(from_date, room, True)

"""
Function that converts raw data to a csv.
    Args:
        from_date: Date of the data.
        room: Dict containing information regarding the room that the data is converted from.
    Returns:
        A dataframe containing the raw data.
"""
def get_raw_data_as_df(from_date: datetime, room: dict) -> pd.DataFrame:
    return convert_csv_to_df(from_date, room, False)


"""
Function that converts the pre-processed data to a tensor (mulit-dimensional array).
    Args:
        from_date: Date of the data.
        room: Dict containing information regarding the room that the data is converted from.
    Returns:
        A tensor containing the pre-processed data.
"""
def get_processed_data_as_tensor(from_date: datetime, room: dict) -> torch.Tensor:
    df = get_processed_data_as_df(from_date, room)
    data_tensor = torch.tensor(df[["room_temp", "ambient_temp", "solar_effect", "heating_setpoint", "cooling_setpoint", "occupancy_effect"]].values, dtype=torch.float32)
    return data_tensor






"""
Function that gathers the pre-processed data and converts it to a csv.
    Args:
        from_date: Date of the data.
        room: Dict containing information regarding the room that the data is converted from.
"""
def pre_process_data_for_date(from_data: datetime, room: dict) -> None:
    df = get_raw_data_as_df(from_data, room)
    solar_effect_list = []
    occupancy_effect_list = []

    for index, row in df.iterrows():
        blinds_control_py(row['solar_watt'], row['wind'])
        solar_effect_current = solar_effect(room, row['solar_watt'])
        solar_effect_list.append(solar_effect_current)
        occupancy_effect_list.append(occupancy_effect(row['heating_setpoint'], row['cooling_setpoint'], index, room))

    preprocessed_data = {"time": df["time"],
                 "solar_effect": solar_effect_list,
                 "room_temp": df["room_temp"],
                 "ambient_temp": df["ambient_temp"],
                 "heating_setpoint": df["heating_setpoint"],
                 "cooling_setpoint": df["cooling_setpoint"],
                 "occupancy_effect": occupancy_effect_list}

    df = pd.DataFrame(preprocessed_data)
    df.to_csv('data/'"" + room["name"] + ""'/processed_data/data_' + from_data.strftime("%Y-%m-%d") + '.csv', mode='w')

"""
Function that pre-processes all data in a specific timeframe.
    Args:
        from_date: Start-date of the data.
        to_date: End-date of the data.
        room: Dict containing information regarding the room that the data is converted from.
"""
def preprocess_data_for_all_dates(from_date: str, to_date: str, room: dict) -> None:
    from_date = datetime.strptime(from_date, "%Y-%m-%dT%H:%M:%SZ")
    days = (datetime.strptime(to_date, "%Y-%m-%dT%H:%M:%SZ") - from_date).days
    for i in range(days):
        pre_process_data_for_date(from_date + timedelta(days=i), room)
        print("Preprocessed for day " + str(i + 1) + " / " + str(days))



blinds = 0
blinds_blocked = False

"""
The current control for the solar blinds at BUILD implemented in Python.
Args:
    solar_watt: the amount of solar watt at a given time.
    wind: the amount of wind at a given time.
"""
def blinds_control_py(solar_watt: float, wind: float) -> None:
    global blinds
    global blinds_blocked
    if wind >= 10:
        blinds_blocked = True
    elif wind <= 8:
        blinds_blocked = False
    if blinds_blocked:
        blinds = 0
        return
    if solar_watt > 180:
        blinds = 1
    elif solar_watt < 120:
        blinds = 0

"""
Function that calculates the solar effect based on the blinds, the solar watt,
the g-value of the window and the window size.
Args:
    room: the room id.
    df_watt: the amount of solar watt at a given time.
Returns:
    The solar effect based on the blinds, the solar watt, the g-value and the window size.
"""
def solar_effect(room: dict, df_watt: float) -> float:
    global blinds
    sun_block = 0
    if blinds == 1:
        sun_block = 0.2
    else:
        sun_block = 1
    G = 0.45
    return df_watt * G * room["window_size"] * sun_block


"""
This function calculates the energy effect of the occupancy in the room.
It takes into account the setpoints of the heater and cooler, the time of day, and the occupancy probability distribution of the room.
Args: 
    heating_setpoint: the setpoint of the heater
    cooling_setpoint: the setpoint of the cooler
    time: the time in minutes since midnight
    room: the room object containing the group and prob_dist attributes
Returns: 
    the energy effect of the occupancy in the room
"""
def occupancy_effect(heating_setpoint: float, cooling_setpoint: float, time: int, room: dict) -> float:
    # Energy effect of the occupancy in the room dependent on office or grouproom. Office is more heat because of pcs and other devices.
    energy_people = 150 if room["group"] else 250 
    occupancy = 0

    if cooling_setpoint - heating_setpoint == 1 :

        if (time < 480):
            occupancy = np.random.choice(room["values"], p=room["prob_dist"][0]) # Occupancy probability distribution from 0 to 8 hours
        elif (time < 720):
            occupancy = np.random.choice(room["values"], p=room["prob_dist"][1]) # Occupancy probability distribution from 8 to 12 hours
        elif (time < 960):
            occupancy = np.random.choice(room["values"], p=room["prob_dist"][2]) # Occupancy probability distribution from 12 to 16 hours
        else:
            occupancy = np.random.choice(room["values"], p=room["prob_dist"][3]) # Occupancy probability distribution from 16 to 24 hours
        
        return occupancy * energy_people
    else:
        return 0