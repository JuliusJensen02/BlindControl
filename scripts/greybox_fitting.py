import csv
import os
from datetime import datetime, timedelta

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize

from scripts.data_processing import convert_csv_to_df, remove_outliers, smooth
from scripts.data_to_csv import reset_csv, query_data
from scripts.plot import plot_df

t_r, t_a, s, h_sp = [[], [], [], []]

def predict_for_date(start_time, constants, plot):
    global t_r, t_a, s, h_sp, v
    reset_csv()
    query_data(start_time, 1)
    df = convert_csv_to_df("data/data.csv")
    df = df.sort_values(by="time")
    t_r = df["room_temp"].values
    t_a = df["ambient_temp"].values
    s = df["watt"].values
    h_sp = df["heating_setpoint"].values
    df['temp_predictions'] = predict_temperature(list(constants.values()))
    if plot:
        plot_df(df)
        return
    return df

def get_constants(start_time = "2025-01-01T00:00:00Z", days = 1):
    if os.path.getsize("data/constants_cache.csv") == 0:
        train_for_time_frame(start_time, days)
        df = convert_csv_to_df("data/constants_cache.csv")
    else:
        df = convert_csv_to_df("data/constants_cache.csv")
        if len(df) == 0 or start_time != df['start_time'][0] or days != df['days'][0]:
            train_for_time_frame(start_time, days)
            df = convert_csv_to_df("data/constants_cache.csv")
    return {'alpha_a': df['alpha_a'], 'alpha_s': df['alpha_s'], 'beta_r': df['beta_r'], 'beta_v': df['beta_v']}

def train_for_time_frame(start_time = "2025-01-01T00:00:00Z", days = 1):
    global t_r, t_a, s, h_sp
    time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
    alpha_a, alpha_s, beta_v, beta_r = [0, 0, 0, 0]
    for i in range(days):
        reset_csv()
        query_data(datetime.strftime(time, "%Y-%m-%dT%H:%M:%SZ"), 1)
        df = convert_csv_to_df("data/data.csv")
        df = remove_outliers(df)
        df = smooth(df)

        df = df.sort_values(by="time")
        t_r = df["room_temp"].values
        t_a = df["ambient_temp"].values
        s = df["watt"].values
        h_sp = df["heating_setpoint"].values
        initial_guess = np.array([0.01, 0.001, 0.1, 0.1])
        result = minimize(mean_squared_error, initial_guess, method="COBYQA")

        alpha_a_opt, alpha_s_opt, beta_r_opt, beta_v_opt = result.x
        alpha_a += alpha_a_opt
        alpha_s += alpha_s_opt
        beta_r += beta_r_opt
        beta_v += beta_v_opt

        df['temp_predictions'] = predict_temperature([alpha_a_opt, alpha_s_opt, beta_r_opt, beta_v_opt])
        time = time + timedelta(days=1)

    with open('data/constants_cache.csv', 'w+', newline='') as csvfile:
        fieldnames = ['alpha_a', 'alpha_s', 'beta_r', 'beta_v', 'start_time', 'days']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  # The csv writer.
        writer.writeheader()
        writer.writerow({'alpha_a': alpha_a / days, 'alpha_s': alpha_s/days, 'beta_r': beta_r/days,
                          'beta_v': beta_v/days, 'start_time': start_time, 'days': days})

def temp_derivative(t, T, alpha_a, alpha_s, beta_r, beta_v):
    """
    Differential equation representing temperature change.
    """
    t_idx = int(t)  # Convert continuous time to discrete index
    if t_idx >= len(t_a):  # Ensure we don't go out of bounds
        t_idx = len(t_a) - 1

    solar_impact = solar_effect(s[t_idx])
    heater_impact = heater_effect(h_sp[t_idx], T)
    return (t_a[t_idx] - T) * alpha_a + solar_impact * alpha_s + heater_impact * beta_r + beta_v

def predict_temperature(constants):
    alpha_a, alpha_s, beta_r, beta_v = constants
    t_span = (0, len(t_r) - 1)  # Time range
    t_eval = np.arange(len(t_r))  # Discrete evaluation points

    # Solve the ODE
    sol = solve_ivp(temp_derivative, t_span, [t_r[0]], t_eval=t_eval, args=(alpha_a, alpha_s, beta_r, beta_v))

    return sol.y[0]  # Return the temperature predictions

def mean_squared_error(constants):
    t_r_pred = predict_temperature(constants)
    return np.mean((t_r - t_r_pred) ** 2)

def solar_effect(df_watt):
    G = 0.7
    mean_window_area_group = 4.25
    return df_watt * G * mean_window_area_group

def heater_effect(setpoint, room_temp):
    if room_temp < setpoint:
        return setpoint-room_temp
    else:
        return 1

def ventilation_effect(something):
    return 1