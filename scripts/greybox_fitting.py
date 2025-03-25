from datetime import datetime, timedelta
import numpy as np
from scipy.optimize import minimize
from scripts.data_processing import convert_csv_to_df
from scripts.derivative_constants import cache_constants
from scripts.derivative_functions import predict_temperature, predict_temperature_rk4
import multiprocessing

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
def use_best_optimization_method(room, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint, lux, best_method, wind):
    best_error = float("inf")
    best_result = None
    optimization_methods = [
        #'L-BFGS-B',
        'TNC',
        #'COBYLA',
        #'SLSQP'
    ]
    best_method[0] = 'TNC'
    bounds = [(0, 1), (0, 1), (0, 1), (0, 1), (0, 1)]  # Bounds for the constants
    if best_method[0] is None:
        print("Choosing best optimization algorithm...")
        for method in optimization_methods:
            #Calculate the best fit for the constants based on the given method and save the best method in result
            result = minimize(sum_squared_error, np.array([0.0001, 0.0001, 0.001, 0.01, 0.0001]), method=method, bounds=bounds, args=(room, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint, lux, wind))
            #Check if the error is less than the best error
            if result.fun < best_error:
                #Set the best error and best method
                best_error = result.fun
                best_method[0] = method
                best_result = result
        print("Best method: ", best_method)
    else:
        best_result = minimize(sum_squared_error, np.array([0.00001, 0.00001, 0.0001, 0.001, 0.00001]), method=best_method[0], bounds=bounds, args=(room, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint, lux, wind))
    return best_result

def train_for_day(room, i, time, best_method, days):
    print("Minimizing for day "+str(i+1)+" / "+str(days))
    """
    Train the model for a specific day (used for multiprocessing).
    """
    df = convert_csv_to_df(time, room)
    room_temp = df["room_temp"].to_numpy()
    ambient_temp = df["ambient_temp"].to_numpy()
    solar_watt = df["solar_watt"].to_numpy()
    heating_setpoint = df["heating_setpoint"].to_numpy()
    cooling_setpoint = df["cooling_setpoint"].to_numpy()
    lux = df["lux"].to_numpy()
    wind = df["wind"].to_numpy()

    result = use_best_optimization_method(room, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint, lux,
                                          best_method, wind)
    # Return results to accumulate constants
    return result.x[0], result.x[1], result.x[2], result.x[3], result.x[4], result.fun

"""
@params start_time: start time as a string
@params days: number of days to train for
Trains the constants for the given timeframe
"""
def train_for_time_frame(room, start_time = "2025-01-01T00:00:00Z", days = 1):
    time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ") #Convert the start time to a datetime object
    alpha_a, alpha_s, alpha_v, alpha_r, alpha_o, error = [0, 0, 0, 0, 0, 0] #Initial constants
    best_method = [None]

    # Create a pool of workers for parallelization
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        # Map the days to the pool workers
        results = pool.starmap(train_for_day, [(room, i, time + timedelta(days=i), best_method, days) for i in range(days)])

    for res in results:
        alpha_a += res[0]
        alpha_s += res[1]
        alpha_r += res[2]
        alpha_v += res[3]
        alpha_o += res[4]
        error += res[5]

    #Calculate the average of the constants and cache them
    cache_constants(alpha_a/days, alpha_s/days, alpha_r/days, alpha_v/days, alpha_o/days, start_time, days, error/days, "data/" + room["name"] + "/constants_cache.csv")


"""
@params constants: list of constants
@params room_temp: list of room temperatures
@params ambient_temp: list of ambient temperatures
@params solar_watt: list of solar_watt
@params heating_setpoint: list of heating setpoints
@params cooling_setpoint: list of cooling setpoints
@returns: mean squared error
Function for calculating the sum squared error
"""
def sum_squared_error(constants, room, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint, lux, wind):
    t_r_pred = predict_temperature(room, constants, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint, lux, wind)
    return np.sum((room_temp - t_r_pred) ** 2)
