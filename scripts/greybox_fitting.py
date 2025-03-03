import csv
import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from scripts.data_processing import convert_csv_to_df, remove_outliers, smooth
from scripts.data_to_csv import reset_csv, query_data
from scripts.derivative_functions import predict_temperature


def get_constants(start_time = "2025-01-01T00:00:00Z", days = 1, retrain = False):
    if os.path.getsize("data/constants_cache.csv") == 0 or retrain:
        train_for_time_frame(start_time, days)
        df = pd.read_csv("data/constants_cache.csv")
    else:
        df = pd.read_csv("data/constants_cache.csv")
        if len(df) == 0 or start_time != df['start_time'][0] or days != df['days'][0]:
            train_for_time_frame(start_time, days)
            df = pd.read_csv("data/constants_cache.csv")
    return {'alpha_a': df['alpha_a'][0], 'alpha_s': df['alpha_s'][0], 'alpha_r': df['alpha_r'][0], 'alpha_v': df['alpha_v'][0]}


def determine_optimization_method(optimization_methods, initial_guess, bounds, room_temp, ambient_temp, watt, opening_signal):
    best_error = float("inf")
    best_method = ""
    for method in optimization_methods:
        initial_guess_dup = initial_guess
        result = minimize(mean_squared_error, initial_guess_dup, method=method, bounds=bounds, args=(room_temp, ambient_temp, watt, opening_signal))
        if result.fun < best_error:
            best_error = result.fun
            best_method = method
    return best_method

def cache_constants(alpha_a, alpha_s, alpha_r, alpha_v, start_time, days):
    with open('data/constants_cache.csv', 'w+', newline='') as csvfile:
        fieldnames = ['alpha_a', 'alpha_s', 'alpha_r', 'alpha_v', 'start_time', 'days']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  # The csv writer.
        writer.writeheader()
        writer.writerow({'alpha_a': alpha_a / days, 'alpha_s': alpha_s/days, 'alpha_r': alpha_r/days,
                          'alpha_v': alpha_v/days, 'start_time': start_time, 'days': days})

def train_for_time_frame(start_time = "2025-01-01T00:00:00Z", days = 1):
    time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
    alpha_a, alpha_s, alpha_v, alpha_r = [0, 0, 0, 0]
    optimization_methods = [
        'Powell',
        'L-BFGS-B',
        'TNC',
        'COBYLA',
        'SLSQP',
        'trust-constr'
    ]
    bounds = [(0, 1), (0, 1), (0, 1), (0, 1)]
    initial_guess = np.array([0.01, 0.001, 0.01, 0.01])
    best_method = None

    for i in range(days):
        reset_csv()
        query_data(datetime.strftime(time, "%Y-%m-%dT%H:%M:%SZ"), 1)
        df = convert_csv_to_df("data/data.csv")
        df = remove_outliers(df)
        df = smooth(df)
        room_temp = df["room_temp"].values
        ambient_temp = df["ambient_temp"].values
        watt = df["watt"].values
        opening_signal = df["opening_signal"].values

        if best_method is None:
            best_method = determine_optimization_method(optimization_methods, initial_guess, bounds, room_temp, ambient_temp, watt, opening_signal)

        result = minimize(mean_squared_error, initial_guess, method=best_method, bounds=bounds, args=(room_temp, ambient_temp, watt, opening_signal))

        alpha_a += result.x[0]
        alpha_s += result.x[1]
        alpha_r += result.x[2]
        alpha_v += result.x[3]

        time = time + timedelta(days=1)

    cache_constants(alpha_a, alpha_s, alpha_r, alpha_v, start_time, days)

def mean_squared_error(constants, room_temp, ambient_temp, watt, opening_signal):
    t_r_pred = predict_temperature(constants, room_temp, ambient_temp, watt, opening_signal)
    return np.mean((room_temp - t_r_pred) ** 2)