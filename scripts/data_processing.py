import numpy as np
import pandas as pd

'''
@param df: DataFrame
@return df: DataFrame
This function normalizes the columns 'watt', 'room_temp', and 'ambient_temp' in the dataframe.
The normalization is done using the formula:
(x - min(x)) / (max(x) - min(x))
where x is the column to be normalized.
'''
def normalize(df):
    # Define the columns to be normalized:
    cols_to_normalize = ['watt', 'room_temp', 'ambient_temp']
    # Using the formula to normalize the columns:
    df[cols_to_normalize] = 20 + (df[cols_to_normalize] - df[cols_to_normalize].min()) / (
                df[cols_to_normalize].max() - df[cols_to_normalize].min())
    # Return the normalized dataframe:
    return df


'''
@param df: DataFrame
@return df_cleaned: DataFrame
This function removes outliers from the dataframe.
The outliers are detected using the rolling mean and the standard deviation of the columns 'watt' and 'room_temp'.
The threshold for the outliers is set to 3 times the standard deviation.
'''
def remove_outliers(df=pd.DataFrame()):
    temp_df = pd.DataFrame()

    # Calculate the rolling mean for the column 'watt':
    temp_df['watt_rolling_mean'] = df['watt'].rolling(window=10, center=True, min_periods=1).mean()

    # Calculate the absolute difference between the actual value and the rolling mean for the column 'watt':
    temp_df['watt_diff'] = np.abs(df['watt'] - temp_df['watt_rolling_mean'])

    # Calculate the rolling mean for the column 'room_temp':
    temp_df['room_temp_rolling_mean'] = df['room_temp'].rolling(window=10, center=True, min_periods=1).mean()

    # Calculate the absolute difference between the actual value and the rolling mean for the column 'room_temp':
    temp_df['room_temp_diff'] = np.abs(df['room_temp'] - temp_df['room_temp_rolling_mean'])

    # Calculate the threshold for the outliers:
    # The threshold is set to 3 times the standard deviation, found using "std()" of the columns 'watt_diff' and 'room_temp_diff':
    threshold_watt = temp_df['watt_diff'].std() * 3
    threshold_room_temp = temp_df['room_temp_diff'].std() * 3

    # Find the outliers using the threshold:
    outliers_ts = df[(temp_df['watt_diff'] > threshold_watt) | (temp_df['room_temp_diff'] > threshold_room_temp)]

    # Remove the outliers from the dataframe:
    df_cleaned = df.drop(outliers_ts.index)

    return df_cleaned


'''
@param csv_data: str
@return df: DataFrame
This function converts the csv data into a DataFrame.
'''
def convert_csv_to_df(csv_data):
    # Read the csv data into a DataFrame:
    # The csv-data is the path to the csv file containing the data.
    df = pd.read_csv(csv_data)
    df = df.sort_values(by="time")
    return df


'''
@param df: DataFrame
@return df: DataFrame
This function smoothes the column 'room_temp' in the dataframe using the rolling mean.
This ensures that the data is less noisy and easier to work with.
'''
def smooth(df):
    # Calculate the rolling mean for the column 'room_temp':
    # Rolling works by taking the average of a window of values around the current value.
    df['room_temp'] = df['room_temp'].rolling(window=15, center=True, min_periods=1).mean()
    return df