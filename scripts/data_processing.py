from datetime import datetime, timedelta
import pandas as pd
import torch

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
Function that gathers the pre-processed data and converts it to a csv.
    Args:
        from_date: Date of the data.
        room: Dict containing information regarding the room that the data is converted from.
"""
def pre_process_data_for_date(from_data: datetime, room: dict) -> None:
    from scripts.new_derivative_functions import occupancy_effect, solar_effect, blinds_control_py
    df = get_raw_data_as_df(from_data, room)
    solar_effect_list = []
    occupancy_effect_list = []

    for index, row in df.iterrows():
        blinds_control_py(row['solar_watt'], row['wind'])
        solar_effect_current = solar_effect(room, row['solar_watt'])
        solar_effect_list.append(solar_effect_current)
        occupancy_effect_list.append(max(occupancy_effect(row['lux']) - solar_effect_current, 0))

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