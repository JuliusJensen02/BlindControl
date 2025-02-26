import numpy as np
import pandas as pd

def normalize(df):
    cols_to_normalize = ['watt', 'room_temp', 'ambient_temp']
    df[cols_to_normalize] = (df[cols_to_normalize] - df[cols_to_normalize].min()) / (df[cols_to_normalize].max() - df[cols_to_normalize].min())
    return df

def remove_outliers(df = pd.DataFrame()):
    temp_df = pd.DataFrame()

    temp_df['watt_rolling_mean'] = df['watt'].rolling(window=10, center=True, min_periods=1).mean()
    temp_df['watt_diff'] = np.abs(df['watt'] - temp_df['watt_rolling_mean'])
    
    temp_df['room_temp_rolling_mean'] = df['room_temp'].rolling(window=10, center=True, min_periods=1).mean()
    temp_df['room_temp_diff'] = np.abs(df['room_temp'] - temp_df['room_temp_rolling_mean'])

    threshold_watt = temp_df['watt_diff'].std() * 3
    threshold_room_temp = temp_df['room_temp_diff'].std() * 3

    outliers_ts = df[(temp_df['watt_diff'] > threshold_watt) | (temp_df['room_temp_diff'] > threshold_room_temp)]
    df_cleaned = df.drop(outliers_ts.index)

    return df_cleaned


def convert_csv_to_df(csv_data):
    df = pd.read_csv(csv_data)
    return df