import csv
import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from scripts.data_processing import convert_csv_to_df, remove_outliers, smooth
from scripts.data_to_csv import reset_csv, query_data, cache_constants
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
@params initial_guess: initial guess for the constants
@params bounds: bounds for the constants
@params room_temp: room temperature values
@params ambient_temp: ambient temperature values
@params solar_watt: solar_watt values
@params heating_setpoint: heating setpoint values
@params cooling_setpoint: cooling setpoint values
@params best_method: the best optimization method
@returns: the best optimization fit
Determines and uses the best minimize method for the minimize function based on the first date
'''
def use_best_optimization_method(initial_guess, bounds, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint, best_method):
    best_error = float("inf")
    best_result = None
    optimization_methods = [
        'Powell',
        'L-BFGS-B',
        'TNC',
        'COBYLA',
        'SLSQP',
        'trust-constr'
    ]
    if best_method is not None:
        for method in optimization_methods:
            initial_guess_dup = initial_guess
            #Calculate the best fit for the constants based on the given method and save the best method in result
            result = minimize(mean_squared_error, initial_guess_dup, method=method, bounds=bounds, args=(room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint))
            #Check if the error is less than the best error
            if result.fun < best_error:
                #Set the best error and best method
                best_error = result.fun
                best_method = method
                best_result = result
    else:
        best_result = minimize(mean_squared_error, initial_guess, method=best_method, bounds=bounds, args=(room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint))
    return best_result

'''
@params start_time: start time as a string
@params days: number of days to train for
Trains the constants for the given timeframe
'''
def train_for_time_frame(start_time = "2025-01-01T00:00:00Z", days = 1):
    time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ") #Convert the start time to a datetime object
    alpha_a, alpha_s, alpha_v, alpha_r, error = [0, 0, 0, 0, 0] #Initial constants
    bounds = [(0, 1), (0, 1), (0, 1), (0, 1)] #Bounds for the constants
    initial_guess = np.array([0.01, 0.001, 0.01, 0.01]) #Initial guess for the constants (Not based on anything)
    best_method = None

    #Train for the given timeframe day by day
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
        solar_watt = df["solar_watt"].values
        heating_setpoint = df["heating_setpoint"].values
        cooling_setpoint = df["cooling_setpoint"].values

        #Calculate the best optimization
        result = use_best_optimization_method(initial_guess, bounds, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint, best_method)

        #Accumulate the constants for the given timeframe
        alpha_a += result.x[0]
        alpha_s += result.x[1]
        alpha_r += result.x[2]
        alpha_v += result.x[3]
        error += result.fun

        #Increment the time by one day
        time = time + timedelta(days=1)

    #Calculate the average of the constants and cache them
    cache_constants(alpha_a/days, alpha_s/days, alpha_r/days, alpha_v/days, start_time, days, error/days)


'''
@params constants: list of constants
@params room_temp: list of room temperatures
@params ambient_temp: list of ambient temperatures
@params solar_watt: list of solar_watt
@params heating_setpoint: list of heating setpoints
@params cooling_setpoint: list of cooling setpoints
@returns: mean squared error
Function for calculating the mean squared error
'''
def mean_squared_error(constants, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint):
    t_r_pred = predict_temperature(constants, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint)
    return np.mean((room_temp - t_r_pred) ** 2)