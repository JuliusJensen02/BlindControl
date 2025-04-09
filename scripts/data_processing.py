from datetime import datetime, timedelta
import pandas as pd
import torch

'''
@param csv_data: str
@return df: DataFrame
This function converts the csv data into a DataFrame.
'''
def convert_csv_to_df(from_date: datetime, room: dict, processed_data = False):
    # Read the csv data into a DataFrame:
    # The csv-data is the path to the csv file containing the data.
    data_path = "query_data"
    if processed_data:
        data_path = "processed_data"
    df = pd.read_csv('data/'"" + room["name"] + ""'/' + data_path + '/data_' + from_date.strftime("%Y-%m-%d") + '.csv')
    df = df.sort_values(by="time")
    return df


'''
@param df: DataFrame
@return df: DataFrame
This function smoothes the column 'room_temp' in the dataframe using the rolling mean.
This ensures that the data is less noisy and easier to work with.
'''
def smooth(df, col):
    # Calculate the rolling mean for the column 'room_temp':
    # Rolling works by taking the average of a window of values around the current value.
    df[col] = df[col].rolling(window=15, center=True, min_periods=1).mean()
    return df


def get_processed_data_as_df(from_date: datetime, room: dict):
    return convert_csv_to_df(from_date, room, True)


def get_raw_data_as_df(from_date: datetime, room: dict):
    return convert_csv_to_df(from_date, room, False)


def pre_process_data_for_date(from_data: datetime, room: dict):
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

def preprocess_data_for_all_dates(from_date: str, to_date: str, room: dict):
    from_date = datetime.strptime(from_date, "%Y-%m-%dT%H:%M:%SZ")
    days = (datetime.strptime(to_date, "%Y-%m-%dT%H:%M:%SZ") - from_date).days
    for i in range(days):
        pre_process_data_for_date(from_date + timedelta(days=i), room)
        print("Preprocessed for day " + str(i + 1) + " / " + str(days))


def get_processed_data_as_tensor(from_date: datetime, room: dict):
    df = get_processed_data_as_df(from_date, room)
    data_tensor = torch.tensor(df[["room_temp", "ambient_temp", "solar_effect", "heating_setpoint", "cooling_setpoint", "occupancy_effect"]].values, dtype=torch.float32)
    return data_tensor