"""
@params alpha_a: alpha_a constant for ambient temperature
@params alpha_s: alpha_s constant for solar effect
@params alpha_r: alpha_r constant for heater effect
@params alpha_v: alpha_v constant for ventilation effect
@params start_time: start time as a string
@params days: number of days to train for
Writes the constants from the training to the cache csv file
"""
import csv
import os

import pandas as pd

from greybox_fitting import train_for_time_frame


def cache_constants(alpha_a, alpha_s, alpha_r, alpha_v, alpha_o, start_time, days, error, path = 'data/constants_cache.csv'):
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
@params start_time: start time as a string
@params days: number of days to train for
@params retrain: boolean for retraining
@returns: dictionary of constants
Function for getting the constants based on the given timeframe
"""
def get_constants(room, start_time = "2025-01-01T00:00:00Z", days = 1, retrain = False, path = "data/constants_cache.csv"):
    #Check if the cache file is empty or if retrain is true
    if os.path.getsize(path) == 0 or retrain:
        train_for_time_frame(room, start_time, days) #Train for the given timeframe
        df = pd.read_csv(path) #Read the cache file
    else:
        df = pd.read_csv(path)
        #Check if valid data is loaded from the cache file to the dataframe and if the start time and days are the same as in the csv file
        if len(df) == 0 or start_time != df['start_time'][0] or days != df['days'][0]:
            train_for_time_frame(room, start_time, days)
            df = pd.read_csv(path)
    #Return the constants as a dictionary
    return {'alpha_a': df['alpha_a'][0], 'alpha_s': df['alpha_s'][0], 'alpha_r': df['alpha_r'][0],
            'alpha_v': df['alpha_v'][0], 'alpha_o': df['alpha_o'][0]}