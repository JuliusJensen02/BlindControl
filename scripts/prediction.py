from datetime import datetime

import pandas as pd
import torch
import torchdiffeq

from scripts.get_simulation_data import convert_uppaal_to_df
from scripts.ODE import TemperatureODE
from scripts.data_processing import get_raw_data_as_df, get_processed_data_as_tensor

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
def simulate_with_resets(ode_class: object, T_r: float, y0, t_points, reset_interval: int) -> torch.Tensor:
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
        current_y = T_r[min(i + reset_interval, len(T_r) - 1)]

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
def predict_for_date(room: dict, start_time: str, prediction_interval: int, period: str) -> pd.DataFrame | None:
    start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
    data = get_processed_data_as_tensor(start_time, room)
    T_r = data[:, 0]  # Room temperature
    T_a = data[:, 1]  # Ambient temperature
    S_t = data[:, 2]  # Solar effect
    h_s = data[:, 3]  # Heating setpoint
    c_s = data[:, 4]  # Cooling setpoint
    O = data[:, 5]    # Occupancy effect
    constants = torch.tensor(room["constants"][period][prediction_interval])  # Convert constants to tensor

    ode_func = TemperatureODE(T_a, S_t, h_s, c_s, O, constants, room["heater_effect"])
    y0 = T_r[0]  # Initial temperature
    t = torch.arange(len(T_r)).float()  # Time points for the simulation

    T_pred = simulate_with_resets(ode_func, T_r, y0, t, reset_interval=prediction_interval)

    df = get_raw_data_as_df(start_time, room)
    df['temp_predictions'] = T_pred

    return df