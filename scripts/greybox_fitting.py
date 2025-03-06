import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scripts.data_processing import convert_csv_to_df
from scripts.data_to_csv import cache_constants
from scripts.derivative_functions import predict_temperature
import multiprocessing
'''
@params start_time: start time as a string
@params days: number of days to train for
@params retrain: boolean for retraining
@returns: dictionary of constants
Function for getting the constants based on the given timeframe
'''
def get_constants(start_time = "2025-01-01T00:00:00Z", days = 1, retrain = False, path = "data/constants_cache.csv"):
    #Check if the cache file is empty or if retrain is true
    if os.path.getsize(path) == 0 or retrain: 
        train_for_time_frame(start_time, days) #Train for the given timeframe
        df = pd.read_csv(path) #Read the cache file
    else:
        df = pd.read_csv(path) 
        #Check if valid data is loaded from the cache file to the dataframe and if the start time and days are the same as in the csv file
        if len(df) == 0 or start_time != df['start_time'][0] or days != df['days'][0]:
            train_for_time_frame(start_time, days)
            df = pd.read_csv(path)
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
def use_best_optimization_method(room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint, best_method):
    best_error = float("inf")
    best_result = None
    optimization_methods = [
        #'L-BFGS-B',
        'TNC',
        #'COBYLA',
        #'SLSQP'
    ]
    best_method[0] = 'TNC'
    t_span = (0, len(room_temp) - 1)  # Time range
    t_eval = np.arange(len(room_temp))  # Discrete evaluation points
    bounds = [(0, 1), (0, 1), (0, 1), (0, 1)]  # Bounds for the constants
    if best_method[0] is None:
        print("Choosing best optimization algorithm...")
        for method in optimization_methods:
            #Calculate the best fit for the constants based on the given method and save the best method in result
            result = minimize(mean_squared_error, np.array([0.01, 0.001, 0.01, 0.01]), method=method, bounds=bounds, args=(t_span, t_eval, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint))
            #Check if the error is less than the best error
            if result.fun < best_error:
                #Set the best error and best method
                best_error = result.fun
                best_method[0] = method
                best_result = result
        print("Best method: ", best_method)
    else:
        best_result = minimize(mean_squared_error, np.array([0.01, 0.001, 0.01, 0.01]), method=best_method[0], bounds=bounds, args=(t_span, t_eval, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint))
    return best_result

def train_for_day(i, time, best_method, days):
    print("Minimizing for day "+str(i+1)+" / "+str(days))
    """
        Train the model for a specific day (used for multiprocessing).
        """
    df = convert_csv_to_df(time)
    room_temp = df["room_temp"].to_numpy()
    ambient_temp = df["ambient_temp"].to_numpy()
    solar_watt = df["solar_watt"].to_numpy()
    heating_setpoint = df["heating_setpoint"].to_numpy()
    cooling_setpoint = df["cooling_setpoint"].to_numpy()

    result = use_best_optimization_method(room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint,
                                          best_method)

    # Return results to accumulate constants
    return result.x[0], result.x[1], result.x[2], result.x[3], result.fun

'''
@params start_time: start time as a string
@params days: number of days to train for
Trains the constants for the given timeframe
'''
def train_for_time_frame(start_time = "2025-01-01T00:00:00Z", days = 1):
    time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ") #Convert the start time to a datetime object
    alpha_a, alpha_s, alpha_v, alpha_r, error = [0, 0, 0, 0, 0] #Initial constants
    best_method = [None]

    # Create a pool of workers for parallelization
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        # Map the days to the pool workers
        results = pool.starmap(train_for_day, [(i, time + timedelta(days=i), best_method, days) for i in range(days)])

    for res in results:
        alpha_a += res[0]
        alpha_s += res[1]
        alpha_r += res[2]
        alpha_v += res[3]
        error += res[4]

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
def mean_squared_error(constants, t_span, t_eval, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint):
    t_r_pred = predict_temperature(constants, t_span, t_eval, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint)
    return np.mean((room_temp - t_r_pred) ** 2)