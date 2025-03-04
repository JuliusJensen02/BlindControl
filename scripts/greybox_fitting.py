import csv
import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from scripts.data_processing import convert_csv_to_df, remove_outliers, smooth
from scripts.data_to_csv import reset_csv, query_data
from scripts.derivative_functions import predict_temperature

'''
@params start_time: start time as a string
@params days: number of days to train for
@params retrain: boolean for retraining
@returns: dictionary of constants
Function for getting the constants based on the given timeframe
'''
def get_constants(start_time = "2025-01-01T00:00:00Z", days = 1, retrain = False):
    #Check if the cache file is empty or if retrain is true
    if os.path.getsize("data/constants_cache.csv") == 0 or retrain: 
        train_for_time_frame(start_time, days) #Train for the given timeframe
        df = pd.read_csv("data/constants_cache.csv") #Read the cache file
    else:
        df = pd.read_csv("data/constants_cache.csv") 
        #Check if valid data is loaded from the cache file to the dataframe and if the start time and days are the same as in the csv file
        if len(df) == 0 or start_time != df['start_time'][0] or days != df['days'][0]:
            train_for_time_frame(start_time, days)
            df = pd.read_csv("data/constants_cache.csv")
    #Return the constants as a dictionary
    return {'alpha_a': df['alpha_a'][0], 'alpha_s': df['alpha_s'][0], 'alpha_r': df['alpha_r'][0], 'alpha_v': df['alpha_v'][0]}


'''
@params optimization_methods: list of available optimization methods
@params initial_guess: initial guess for the constants
@params bounds: bounds for the constants
@params room_temp: room temperature values
@params ambient_temp: ambient temperature values
@params watt: watt values
@params opening_signal: opening signal values
@returns: the best optimization method
Determines the best minimize method for the minimize function based on the first date
'''
def determine_optimization_method(optimization_methods, initial_guess, bounds, room_temp, ambient_temp, watt, opening_signal):
    best_error = float("inf")
    best_method = ""
    for method in optimization_methods:
        initial_guess_dup = initial_guess
        #Calculate the best fit for the constants based on the given method and save the best method in result
        result = minimize(mean_squared_error, initial_guess_dup, method=method, bounds=bounds, args=(room_temp, ambient_temp, watt, opening_signal))
        #Check if the error is less than the best error
        if result.fun < best_error:
            #Set the best error and best method
            best_error = result.fun
            best_method = method
    return best_method

'''
@params alpha_a: alpha_a constant for ambient temperature
@params alpha_s: alpha_s constant for solar effect
@params alpha_r: alpha_r constant for heater effect
@params alpha_v: alpha_v constant for ventilation effect
@params start_time: start time as a string
@params days: number of days to train for
Writes the constants from the training to the cache csv file
'''
def cache_constants(alpha_a, alpha_s, alpha_r, alpha_v, start_time, days):
    #Open the csv file in write mode
    with open('data/constants_cache.csv', 'w+', newline='') as csvfile:
        fieldnames = ['alpha_a', 'alpha_s', 'alpha_r', 'alpha_v', 'start_time', 'days'] # The fieldnames for the csv file.
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  # The csv writer.
        writer.writeheader()
        #Write the constants to the csv file
        writer.writerow({'alpha_a': alpha_a, 'alpha_s': alpha_s, 'alpha_r': alpha_r,
                          'alpha_v': alpha_v, 'start_time': start_time, 'days': days})


'''
@params start_time: start time as a string
@params days: number of days to train for
Trains the constants for the given timeframe
'''
def train_for_time_frame(start_time = "2025-01-01T00:00:00Z", days = 1):
    time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ") #Convert the start time to a datetime object
    alpha_a, alpha_s, alpha_v, alpha_r = [0, 0, 0, 0] #Initial constants
    optimization_methods = [
        'Powell',
        'L-BFGS-B',
        'TNC',
        'COBYLA',
        'SLSQP',
        'trust-constr'
    ]
    bounds = [(0, 1), (0, 1), (0, 1), (0, 1)] #Bounds for the constants
    initial_guess = np.array([0.01, 0.001, 0.01, 0.01]) #Initial guess for the constants (Not based on anything)
    best_method = None

    #Train for the given timeframe
    for i in range(days):
        #Reset the csv file
        reset_csv()

        #Query the data for the given date
        query_data(datetime.strftime(time, "%Y-%m-%dT%H:%M:%SZ"), 1)

        df = convert_csv_to_df("data/data.csv")         #Convert the csv file data to a dataframe
        df = remove_outliers(df)                        #Remove outliers from the dataframe
        df = smooth(df)                                 #Smooth the dataframe

        #Save the values of the columns in the dataframe to variables
        room_temp = df["room_temp"].values
        ambient_temp = df["ambient_temp"].values
        watt = df["watt"].values
        opening_signal = df["opening_signal"].values

        #Determine the best method using the determine_optimization_method function
        #TODO: Make determine_optimization_method return result instead of best_method, to avoid a run of the minimize function
        if best_method is None:
            best_method = determine_optimization_method(optimization_methods, initial_guess, bounds, room_temp, ambient_temp, watt, opening_signal)

        #Calculate the best fit for the constants based on the best method (Again??!?)
        result = minimize(mean_squared_error, initial_guess, method=best_method, bounds=bounds, args=(room_temp, ambient_temp, watt, opening_signal))

        #Accumulate the constants for the given timeframe
        alpha_a += result.x[0]
        alpha_s += result.x[1]
        alpha_r += result.x[2]
        alpha_v += result.x[3]

        #Increment the time by one day
        time = time + timedelta(days=1)

    #Calculate the average of the constants and cache them
    cache_constants(alpha_a/days, alpha_s/days, alpha_r/days, alpha_v/days, start_time, days)


'''
@params constants: list of constants
@params room_temp: list of room temperatures
@params ambient_temp: list of ambient temperatures
@params watt: list of watt
@params opening_signal: list of opening signals
@returns: mean squared error
Function for calculating the mean squared error
'''
def mean_squared_error(constants, room_temp, ambient_temp, watt, opening_signal):
    t_r_pred = predict_temperature(constants, room_temp, ambient_temp, watt, opening_signal)
    return np.mean((room_temp - t_r_pred) ** 2)