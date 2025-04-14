import csv
import os
import pandas as pd
from scripts.training import train_for_time_frame

"""
Writes the constants from the training to the cache csv file.
Args:
    alpha_a: alpha_a constant for ambient temperature.
    alpha_s: alpha_s constant for solar effect.
    alpha_r: alpha_r constant for heater effect.
    alpha_v: alpha_v constant for ventilation effect.
    start_time: start time as a string.
    days: number of days to train for.
    error: the error value extracted from the training.
    path: the path of the cache.csv file.
"""
def cache_constants(alpha_a: float, alpha_s: float, alpha_r: float, alpha_v: float, alpha_o: float,
                    start_time: str, days: int, error: float, path: str):
    #Open the csv file in write mode
    with open(path, 'w+', newline='') as csvfile:
        fieldnames = ['alpha_a', 'alpha_s', 'alpha_r', 'alpha_v', 'alpha_o', 'start_time', 'days', 'error'] # The fieldnames for the csv file.
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  # The csv writer.
        writer.writeheader()
        #Write the constants to the csv file
        writer.writerow({'alpha_a': alpha_a, 'alpha_s': alpha_s, 'alpha_r': alpha_r,
                         'alpha_v': alpha_v, 'alpha_o': alpha_o, 'start_time': start_time,
                         'days': days, 'error': error})



"""
Function for getting the constants based on the given timeframe.
Args:
    room: the room number as a string.
    start_time: start time as a string.
    days: number of days to train for.
    retrain: boolean for retraining.
    prediction_interval: interval for how far ahead the temperature is predicted.
Returns:
    Dictionary of constants.
"""
def get_constants(room: str, start_time: str, days: int, retrain: bool, prediction_interval: int):
    path = "data/" + room["name"] + "/constants_cache.csv"

    if is_retrain_needed(path, start_time, days, retrain):
        print("Retraining...", flush=True)
        constants, error = train_for_time_frame(room, start_time, days, prediction_interval)
        print("Finished training", flush=True)
        print((constants, error), flush=True)
    df = pd.read_csv(path)

    #Return the constants as a dictionary
    return {'alpha_a': df['alpha_a'][0], 'alpha_s': df['alpha_s'][0], 'alpha_r': df['alpha_r'][0],
            'alpha_v': df['alpha_v'][0], 'alpha_o': df['alpha_o'][0]}

"""
A function that evaluates if retraining is necessary, based on whether there is cached data or if 
the retrain parameter is set to true.
Args:
    path: the path of the cache.csv file.
    start_time: start time as a string.
    days: number of days to train for.
    retrain: boolean for retraining.
Returns:
    A boolean indicating if retraining is necessary.
"""
def is_retrain_needed(path: str, start_time: str, days: int, retrain: bool):
    df = pd.read_csv(path)

    # Check if the cache file is empty or if retrain is true
    # Check if valid data is loaded from the cache file to the dataframe and if the start time and days are the same as in the csv file
    if (os.path.getsize(path) == 0 or
            retrain or
            len(df) == 0 or
            start_time != df['start_time'][0] or
            days != df['days'][0]):
        return True
    return False