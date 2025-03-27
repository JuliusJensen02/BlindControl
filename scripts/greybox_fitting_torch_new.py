import torch
import numpy as np
from datetime import datetime, timedelta
from scripts.data_processing import convert_csv_to_df

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Torch-compatible effect functions
def occupancy_effect_torch(lux):
    lpp = 300
    e_p = 100
    return lux / lpp * e_p

def solar_effect_torch(solar_watt, window_size, blinds_state):
    G = 0.45
    sun_block = torch.where(blinds_state == 1, 0.2, 1.0)
    return solar_watt * G * window_size * sun_block

def heater_effect_torch(heating_setpoint, room_temp, max_heat, charge=0.02, decay=0.02):
    envelope = torch.zeros_like(room_temp)
    decay_tensor = torch.tensor(decay, dtype=torch.float32, device=room_temp.device)
    for i in range(1, room_temp.shape[1]):
        is_on = room_temp[:, i - 1] <= heating_setpoint[:, i - 1]
        envelope[:, i] = torch.where(
            is_on,
            torch.clamp(envelope[:, i - 1] + charge * max_heat, max=max_heat),
            envelope[:, i - 1] * torch.exp(-decay_tensor)
        )
    return envelope

def blinds_logic_torch(solar_watt, wind):
    blinds = torch.zeros_like(solar_watt)
    blocked = wind >= 10
    unblocked = wind <= 8
    for i in range(1, solar_watt.shape[1]):
        blinds[:, i] = torch.where(blocked[:, i], 0, blinds[:, i - 1])
        blinds[:, i] = torch.where(~blocked[:, i] & (solar_watt[:, i] > 180), 1, blinds[:, i])
        blinds[:, i] = torch.where(~blocked[:, i] & (solar_watt[:, i] < 120), 0, blinds[:, i])
    return blinds

def simulate_all_days(room, constants, T_r, T_a, solar_watt, heating_setpoint, cooling_setpoint, lux, wind):
    a_a, a_s, a_h, a_v, a_o = constants

    blinds = blinds_logic_torch(solar_watt, wind)
    S_t = solar_effect_torch(solar_watt, room["window_size"], blinds)
    E_h = heater_effect_torch(heating_setpoint, T_r, room["heater_effect"])
    O = torch.clamp(occupancy_effect_torch(lux) - S_t, min=0)

    # Vectorized Euler integration via cumulative sum
    dT = ((T_a[:, 1:] - T_r[:, :-1]) * a_a +
          S_t[:, 1:] * a_s +
          E_h[:, 1:] * a_h +
          (T_a[:, 1:] - T_r[:, :-1]) * a_v +
          O[:, 1:] * a_o)

    T_pred = torch.zeros_like(T_r)
    T_pred[:, 0] = T_r[:, 0]
    T_pred[:, 1:] = T_r[:, 0:1] + torch.cumsum(dT, dim=1)

    return T_pred

def load_batch_data(room, start_time, days):
    time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
    dfs = [convert_csv_to_df(time + timedelta(days=i), room) for i in range(days)]

    def stack(col):
        min_len = min(len(df[col]) for df in dfs)
        return torch.stack([
            torch.tensor(df[col].values[:min_len], dtype=torch.float32, device=device)
            for df in dfs
        ])

    return {
        "T_r": stack("room_temp"),
        "T_a": stack("ambient_temp"),
        "solar_watt": stack("solar_watt"),
        "heating_setpoint": stack("heating_setpoint"),
        "cooling_setpoint": stack("cooling_setpoint"),
        "lux": stack("lux"),
        "wind": stack("wind"),
    }

def train_batch(room, start_time="2025-01-01T00:00:00Z", days=90, lr=0.01, epochs=200):
    data = load_batch_data(room, start_time, days)
    constants = torch.nn.Parameter(torch.rand(5, dtype=torch.float32, device=device))
    optimizer = torch.optim.Adam([constants], lr=lr)

    for epoch in range(epochs):
        optimizer.zero_grad()
        T_pred = simulate_all_days(room, constants, **data)
        loss = torch.mean((T_pred - data["T_r"]) ** 2)
        loss.backward()
        optimizer.step()
        if epoch % 20 == 0:
            print(f"Epoch {epoch}, Loss: {loss.item():.6f}")

    final_constants = constants.detach().cpu().numpy()
    final_error = loss.item()
    from scripts.derivative_constants import cache_constants
    cache_constants(*final_constants, start_time, days, final_error, f"data/{room['name']}/constants_cache.csv")
    return final_constants, final_error
