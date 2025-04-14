from datetime import datetime

import pandas as pd
import torch
import torchdiffeq

from experiments.uppaal_jobs.plot_simulation_data import convert_uppaal_to_df
from scripts.ODE import TemperatureODE
from scripts.data_processing import get_raw_data_as_df, get_processed_data_as_tensor
from scripts.plot import plot_df

"""
Function that simulates the room temperature.
Args:
    ode_class: Class with the values needed to predict the temperature.
    T_r: The room temperature.
    y0: The initial state of the simulation.
    t_points: Tensor of time points used to simulate the temperature.
    reset_interval: The interval with which to reset the simulation.
Returns:
    A tensor with the predicted temperatures and time.
"""
def simulate_with_resets(ode_class: object, T_r: float, y0, t_points, reset_interval: int):
    results = []
    current_y = y0.clone()

    for i in range(0, len(t_points), reset_interval):
        t_seg = t_points[i:i + reset_interval + 1]
        if len(t_seg) < 2:
            break

        y_seg = torchdiffeq.odeint(ode_class, current_y, t_seg, method="euler")
        if i + reset_interval >= len(t_points) - 1:
            results.append(y_seg)
        else:
            results.append(y_seg[:-1])

        # Reset temperature to real value, continue with simulated heater state
        next_T = T_r[min(i + reset_interval, len(T_r) - 1)]
        next_H = y_seg[-1, 1]
        current_y = torch.stack([next_T, next_H])

    return torch.cat(results, dim=0)


"""
Predicts the temperature for a specific date.
Args:
    room: A dict containing all information about the room.
    start_time: The date for the prediction.
    constants: The constants used to predict the temperature.
    plot: A boolean that decides if the prediction should be plotted.
    prediction_interval: The interval used to reset the prediction of the temperature.
Returns:
    Either plots the prediction or returns a dataframe with the predicted temperatures.
"""
def predict_for_date(room: dict, start_time: str, constants, plot: bool, prediction_interval: int):
    start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
    data = get_processed_data_as_tensor(start_time, room)
    T_r = data[:, 0]  # Room temperature
    T_a = data[:, 1]  # Ambient temperature
    S_t = data[:, 2]  # Solar effect
    h_s = data[:, 3]  # Heating setpoint
    c_s = data[:, 4]  # Cooling setpoint
    O = data[:, 5]    # Occupancy effect
    constants = torch.tensor(constants)  # Convert constants to tensor

    ode_func = TemperatureODE(T_a, S_t, h_s, O, constants, room["heater_effect"])
    T0 = T_r[0]  # Initial temperature
    H0 = torch.tensor(0.0)  # Initial heater state
    y0 = torch.stack([T0, H0])  # Initial state
    t = torch.arange(len(T_r)).float()  # Time points for the simulation

    y = simulate_with_resets(ode_func, T_r, y0, t, reset_interval=prediction_interval)
    T_pred = y[:, 0]

    df = get_raw_data_as_df(start_time, room)
    df['temp_predictions'] = T_pred
    uppaal_df = convert_uppaal_to_df(start_time.strftime("%Y_%m_%d"))
    df = pd.merge(df, uppaal_df, how='left', left_index=True, right_index=True)

    #df['temp_predictions'] = predict_temperature_for_prediction(room, constants.values(), room_temp, ambient_temp, solar_watt,
    #                            heating_setpoint, cooling_setpoint, lux, wind, heating_effects, solar_effects)
    #df['heating_effects'] = heating_effects
    #df['solar_effects'] = solar_effects
    #df = smooth(df, 'temp_predictions')
    #Plot the data if plot is true
    if plot:
        plot_df(df)
        return
    return df