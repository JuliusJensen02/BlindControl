from datetime import datetime, timedelta
import torch
import numpy as np

from data_processing import get_processed_data_as_df
from derivative_functions import heater_effect_torch

def torch_predict_temperature(room, constants, T_r, T_a, S_t, heating_setpoint, cooling_setpoint, O, prediction_interval):
    a_a, a_s, a_h, a_v, a_o = constants

    # Precompute static parameters
    heater_max = room["heater_effect"]

    E_h = heater_effect_torch(heating_setpoint, T_r, heater_max)

    # Initialize result array
    T = torch.zeros_like(T_r)
    T[0] = T_r[0]

    for i in range(1, len(T_r)):
        if i % prediction_interval == 0:
            T[i] = T_r[i]
        else:
            dT = ((T_a[i] - T[i - 1]) * a_a +
                  S_t[i] * a_s +
                  E_h[i] * a_h +
                  (T_a[i] - T[i - 1]) * a_v +
                  O[i] * a_o)
            T[i] = T[i - 1] + dT

    return T


def train_one_day_pytorch(room, df, prediction_interval, lr=5e-6, epochs=800):
    T_r = torch.tensor(df["room_temp"].values, dtype=torch.float32)
    T_a = torch.tensor(df["ambient_temp"].values, dtype=torch.float32)
    S_t = torch.tensor(df["solar_effect"].values, dtype=torch.float32)
    heating_setpoint = torch.tensor(df["heating_setpoint"].values, dtype=torch.float32)
    cooling_setpoint = torch.tensor(df["cooling_setpoint"].values, dtype=torch.float32)
    O = torch.tensor(df["occupancy_effect"].values, dtype=torch.float32)

    #mean_temp = T_r.mean()
    #std_temp = T_r.std()
    #T_r = (T_r - mean_temp) / std_temp

    constants = torch.nn.Parameter(torch.tensor([0.000001, 0.000001, 0.00001, 0.0001, 0.00001], dtype=torch.float32, requires_grad=True))
    optimizer = torch.optim.Adam([constants], lr=lr)

    for epoch in range(epochs):
        optimizer.zero_grad()
        T_pred = torch_predict_temperature(room, constants, T_r, T_a, S_t, heating_setpoint, cooling_setpoint, O, prediction_interval)
        loss = torch.mean((T_pred - T_r) ** 2)
        loss.backward()
        optimizer.step()
        if epoch % 50 == 0:
            print(f"Epoch {epoch}, Loss: {loss.item():.6f}")

    return constants.detach().numpy(), loss.item()

def train_for_time_frame_pytorch(room, start_time="2025-01-01T00:00:00Z", days=1, prediction_interval=10):
    time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
    alpha = np.zeros(5)
    total_error = 0.0

    for i in range(days):
        df = get_processed_data_as_df(time + timedelta(days=i), room)
        constants, error = train_one_day_pytorch(room, df, prediction_interval)
        alpha += constants
        total_error += error
        print(f"Day {i + 1}/{days} done - Loss: {error:.6f}")

    avg_constants = alpha / days
    avg_error = total_error / days
    from scripts.derivative_constants import cache_constants
    cache_constants(*avg_constants, start_time, days, avg_error, f"data/{room['name']}/constants_cache.csv")

    return avg_constants, avg_error


