import os
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta
from math import floor

import numpy as np
import torch

from scripts.data_processing import get_processed_data_as_tensor
from scripts.new_derivative_functions import predict_temperature
torch.autograd.set_detect_anomaly(True)


def train_day(data: torch.Tensor, prediction_interval: int, heater_max: float):
    learning_rate = 5e-7
    epochs = 800

    # Unpack the data
    T_r = data[:, 0] # Room temperature
    T_a = data[:, 1] # Ambient temperature
    S_t = data[:, 2] # Solar effect
    h_s = data[:, 3] # Heating setpoint
    c_s = data[:, 4] # Cooling setpoint
    O = data[:, 5]   # Occupancy effect

    torch.set_num_threads(4)

    constants = torch.nn.Parameter(torch.tensor([0.000001, 0.000001, 0.00001, 0.0001, 0.00001], dtype=torch.float32, requires_grad=True))
    optimizer = torch.optim.Adam([constants], lr=learning_rate)

    for epoch in range(epochs):
        optimizer.zero_grad()
        T_pred = predict_temperature(constants, T_r, T_a, S_t, h_s, c_s, O, prediction_interval, heater_max)
        loss = torch.mean((T_pred - T_r) ** 2)
        loss.backward()
        optimizer.step()
        if epoch % 1 == 0:
            print(f"Epoch {epoch}, Loss: {loss.item():.6f}")

    return constants.detach().numpy(), loss.item()





def _train_day(args: list):
    time, room, prediction_interval = args
    data = get_processed_data_as_tensor(time, room)
    return train_day(data, prediction_interval, room["heater_effect"])





def train_for_time_frame(room: dict, start_time: str, days: int, prediction_interval: int):
    time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ") #Convert start_time to datetime object
    args_list = [(time + timedelta(days=i), room, prediction_interval) for i in range(days)] #Pack the arguments for each day into a list

    alpha = np.zeros(5) # Initialize the constants
    total_error = 0.0   # Initialize the total error

    with ProcessPoolExecutor(max_workers=floor(os.cpu_count() / torch.get_num_threads())) as executor:
        results = executor.map(_train_day, args_list)

        for i, (constants, error) in enumerate(results):
            alpha += constants
            total_error += error
            print(f"Day {i + 1}/{days} done - Loss: {error:.6f}", flush=True)

    avg_constants = alpha / days
    avg_error = total_error / days
    from scripts.constants import cache_constants
    cache_constants(*avg_constants, start_time, days, avg_error, f"data/{room['name']}/constants_cache.csv")

    return avg_constants, avg_error