import math
import torch
import torchdiffeq

blinds = 0
blinds_blocked = False

def blinds_control_py(solar_watt, wind):
    global blinds
    global blinds_blocked
    if wind >= 10:
        blinds_blocked = True
    elif wind <= 8:
        blinds_blocked = False
    if blinds_blocked:
        blinds = 0
        return
    if solar_watt > 180:
        blinds = 1
    elif solar_watt < 120:
        blinds = 0

def solar_effect(room, df_watt):
    global blinds
    sun_block = 0
    if blinds == 1:
        sun_block = 0.2
    else:
        sun_block = 1
    G = 0.45
    return df_watt * G * room["window_size"] * sun_block

@torch.jit.script
def heater_effect(heating_setpoint: float, current_temperature: float, max_heat_stored: float, charge_effect: float, decay_effect: float, heater_envelope: float) -> float:
    if current_temperature <= heating_setpoint:
        heater_envelope = min(heater_envelope + charge_effect * max_heat_stored, max_heat_stored)
    else:
        heater_envelope *= math.exp(-decay_effect)

    return heater_envelope


def occupancy_effect(lux):
    lpp = 300
    e_p = 100
    return lux / lpp * e_p #lpp is lux per person, e_p is wattage per person



def derivative_function(T_a, T_r, a_a, E_h, a_h, a_v, S_t, a_s, O, a_o):
    return ((T_a - T_r) * a_a +
            S_t * a_s +
            E_h * a_h +
            (T_a - T_r) * a_v +
            O * a_o)






@torch.jit.script
def predict_temperature(
    constants: torch.Tensor,
    T_r: torch.Tensor,
    T_a: torch.Tensor,
    S_t: torch.Tensor,
    h_s: torch.Tensor,
    c_s: torch.Tensor,
    O: torch.Tensor,
    prediction_interval: int,
    heater_max: float
) -> torch.Tensor:
    heater_envelope = 0.0

    data_points = T_r.size(0)

    a_a = constants[0]
    a_s = constants[1]
    a_h = constants[2]
    a_v = constants[3]
    a_o = constants[4]

    T = torch.zeros_like(T_r)

    #Loop over the data points in intervals of prediction_interval
    #E.g. if prediction_interval = 60, then the loop will run for 1 to 60, 61 to 120, etc.
    for start in range(0, data_points, prediction_interval+1):
        end = min(start + prediction_interval, data_points)
        T[start] = T_r[start]
        for i in range(start + 1, end):
            heater_envelope = heater_effect(h_s[i].item(), T[i - 1].item(), heater_max, 0.02, 0.02, heater_envelope)
            dT = ((T_a[i] - T[i - 1]) * a_a +
                  S_t[i] * a_s +
                  heater_envelope * a_h +
                  (T_a[i] - T[i - 1]) * a_v +
                  O[i] * a_o)
            T[i] = T[i - 1] + dT

    return T







@torch.jit.script
def predict_temperature_steroid(
    constants: torch.Tensor,
    T_r: torch.Tensor,
    T_a: torch.Tensor,
    S_t: torch.Tensor,
    h_s: torch.Tensor,
    c_s: torch.Tensor,
    O: torch.Tensor,
    prediction_interval: int,
    heater_max: float
) -> torch.Tensor:
    heater_envelope = 0.0

    data_points = T_r.size(0)

    a_a = constants[0]
    a_s = constants[1]
    a_h = constants[2]
    a_v = constants[3]
    a_o = constants[4]

    T = torch.zeros_like(T_r)

    torchdiffeq.odeint(derivative_function, T_r[0], T)

    #Loop over the data points in intervals of prediction_interval
    #E.g. if prediction_interval = 60, then the loop will run for 1 to 60, 61 to 120, etc.
    for start in range(0, data_points, prediction_interval+1):
        end = min(start + prediction_interval, data_points)
        T[start] = T_r[start]
        for i in range(start + 1, end):
            heater_envelope = heater_effect(h_s[i].item(), T[i - 1].item(), heater_max, 0.02, 0.02, heater_envelope)
            dT = ((T_a[i] - T[i - 1]) * a_a +
                  S_t[i] * a_s +
                  heater_envelope * a_h +
                  (T_a[i] - T[i - 1]) * a_v +
                  O[i] * a_o)
            T[i] = T[i - 1] + dT

    return T