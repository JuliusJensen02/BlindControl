from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta
import torch
import numpy as np

from scripts.data_processing import get_processed_data_as_df
import sys
sys.stdout.reconfigure(line_buffering=True)
torch.set_num_threads(4)


@torch.jit.script
def torch_predict_temperature(
    constants: torch.Tensor,
    T_r: torch.Tensor,
    T_a: torch.Tensor,
    S_t: torch.Tensor,
    heating_setpoint: torch.Tensor,
    cooling_setpoint: torch.Tensor,
    O: torch.Tensor,
    prediction_interval: int,
    heater_max: float,
    charge: float = 0.02,
    decay: float = 0.02
) -> torch.Tensor:
    a_a = constants[0]
    a_s = constants[1]
    a_h = constants[2]
    a_v = constants[3]
    a_o = constants[4]

    T = torch.zeros_like(T_r)
    T[0] = T_r[0]

    envelope = torch.zeros_like(T_r)
    decay_tensor = torch.tensor(decay, dtype=torch.float32)
    charge_tensor = torch.tensor(charge, dtype=torch.float32)

    for start in range(0, T_r.size(0), prediction_interval):
        end = min(start + prediction_interval, T_r.size(0))
        T[start] = T_r[start]
        for i in range(start + 1, end):
            # Heater effect step-by-step
            if T[i - 1] <= heating_setpoint[i - 1]:
                envelope[i] = torch.clamp(envelope[i - 1] + charge_tensor * heater_max, max=heater_max)
            else:
                envelope[i] = envelope[i - 1] * torch.exp(-decay_tensor)

            # Temperature update
            dT = ((T_a[i] - T[i - 1]) * a_a +
                  S_t[i] * a_s +
                  envelope[i] * a_h +
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

    constants = torch.nn.Parameter(torch.tensor([0.000001, 0.000001, 0.00001, 0.0001, 0.00001], dtype=torch.float32, requires_grad=True))
    optimizer = torch.optim.Adam([constants], lr=lr)

    for epoch in range(epochs):
        optimizer.zero_grad()
        heater_max = room["heater_effect"]
        T_pred = torch_predict_temperature(constants, T_r, T_a, S_t, heating_setpoint, cooling_setpoint, O, prediction_interval, heater_max)
        loss = torch.mean((T_pred - T_r) ** 2)
        loss.backward()
        optimizer.step()
        if epoch % 50 == 0:
            print(f"Epoch {epoch}, Loss: {loss.item():.6f}", flush=True)
            sys.stdout.flush()

    return constants.detach().numpy(), loss.item()

def train_for_time_frame_pytorch(room, start_time="2025-01-01T00:00:00Z", days=1, prediction_interval=10):
    time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
    alpha = np.zeros(5)
    total_error = 0.0
    print("Training for time frame...", flush=True)
    for i in range(days):
        df = get_processed_data_as_df(time + timedelta(days=i), room)
        constants, error = train_one_day_pytorch(room, df, prediction_interval)
        alpha += constants
        total_error += error
        print(f"Day {i + 1}/{days} done - Loss: {error:.6f}", flush=True)
        sys.stdout.flush()

    avg_constants = alpha / days
    avg_error = total_error / days
    from scripts.derivative_constants import cache_constants
    cache_constants(*avg_constants, start_time, days, avg_error, f"data/{room['name']}/constants_cache.csv")

    return avg_constants, avg_error



def _train_day(args):
    time, room, prediction_interval = args
    df = get_processed_data_as_df(time, room)
    return train_one_day_pytorch(room, df, prediction_interval)




def train_for_time_frame_parallel(room, start_time="2025-01-01T00:00:00Z", days=1, prediction_interval=10):
    time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
    args_list = [(time + timedelta(days=i), room, prediction_interval) for i in range(days)]

    alpha = np.zeros(5)
    total_error = 0.0

    with ProcessPoolExecutor() as executor:
        results = executor.map(_train_day, args_list)

        for i, (constants, error) in enumerate(results):
            alpha += constants
            total_error += error
            print(f"Day {i + 1}/{days} done - Loss: {error:.6f}", flush=True)

    avg_constants = alpha / days
    avg_error = total_error / days
    from scripts.derivative_constants import cache_constants
    cache_constants(*avg_constants, start_time, days, avg_error, f"data/{room['name']}/constants_cache.csv")

    return avg_constants, avg_error
