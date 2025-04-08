from concurrent.futures import ProcessPoolExecutor

import numpy as np
import torch
import torchdiffeq
from datetime import datetime, timedelta

from scripts.ODE import TemperatureODE
from scripts.data_processing import get_processed_data_as_tensor

'''
Reset the temperature to the room temperature value every reset_interval steps.
Args:
    ode_class: The ODE class to be used for simulation.
    T_r: The room temperature values.
    y0: The initial state of the system.
    t_points: The time points at which to evaluate the ODE.
    reset_interval: The interval at which to reset the temperature.
Returns:
    A tensor containing the simulated values of the system.
'''
def simulate_with_resets(ode_class, T_r, y0, t_points, reset_interval):
    results = []
    current_y = y0.clone()

    for i in range(0, len(t_points), reset_interval):
        t_seg = t_points[i:i + reset_interval + 1]
        if len(t_seg) < 2:
            break

        y_seg = torchdiffeq.odeint(ode_class, current_y, t_seg, method="euler")
        results.append(y_seg[:-1])

        # Reset temperature to real value, continue with simulated heater state
        next_T = T_r[min(i + reset_interval, len(T_r) - 1)]
        next_H = y_seg[-1, 1]
        current_y = torch.stack([next_T, next_H])

    return torch.cat(results, dim=0)






'''
Finds the optimal constants for the ODE model by training it on a single day of data.
Args:
    time: The time for which to train the model.
    room: The room data containing the heater effect.
    prediction_interval: The interval at which to reset the temperature.
    step: The step size for the data.
Returns:
    A tuple containing the optimized constants and the loss value.
'''
def train_day(time: datetime, room: dict, prediction_interval: int, step: int = 1):
    data = get_processed_data_as_tensor(time, room)
    T_r = data[:, 0][::step]   # Room temperature
    T_a = data[:, 1][::step]   # Ambient temperature
    S_t = data[:, 2][::step]   # Solar effect
    h_s = data[:, 3][::step]   # Heating setpoint
    c_s = data[:, 4][::step]   # Cooling setpoint
    O = data[:, 5][::step]     # Occupancy effect

    learning_rate = 5e-6
    epochs = 800

    constants = torch.nn.Parameter(torch.tensor([0.000001, 0.000001, 0.00001, 0.0001, 0.00001], dtype=torch.float32, requires_grad=True))
    optimizer = torch.optim.Adam([constants], lr=learning_rate)

    for epoch in range(epochs):
        optimizer.zero_grad() # Clear the gradients

        ode_func = TemperatureODE(T_a, S_t, h_s, O, constants, room["heater_effect"]) # Initialize the ODE class

        T0 = T_r[0] # Initial temperature
        H0 = torch.tensor(0.0) # Initial heater state
        y0 = torch.stack([T0, H0]) # Initial state
        t = torch.arange(len(T_r)).float() # Time points for the simulation

        y = simulate_with_resets(ode_func, T_r, y0, t, reset_interval=prediction_interval)
        T_pred = y[:, 0]

        loss = torch.mean((T_pred - T_r[:len(T_pred)]) ** 2)
        loss.backward()
        optimizer.step()
    return constants.detach().numpy(), loss.item()


def _train_day(args: list):
    time, room, prediction_interval = args
    print("Training for", time.strftime("%Y-%m-%dT%H:%M:%SZ"), flush=True)
    return train_day(time, room, prediction_interval)

def train_for_time_frame(room: dict, start_time: str, days: int, prediction_interval: int):
    time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ") #Convert start_time to datetime object
    args_list = [(time + timedelta(days=i), room, prediction_interval) for i in range(days)] #Pack the arguments for each day into a list

    alpha = np.zeros(5) # Initialize the constants
    total_error = 0.0   # Initialize the total error

    with ProcessPoolExecutor() as executor:
        results = executor.map(_train_day, args_list)

        for i, (constants, error) in enumerate(results):
            alpha += constants
            total_error += error

    avg_constants = alpha / days
    avg_error = total_error / days
    from scripts.derivative_constants import cache_constants
    cache_constants(*avg_constants, start_time, days, avg_error, f"data/{room['name']}/constants_cache.csv")

    return avg_constants, avg_error