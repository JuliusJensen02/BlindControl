import math
import numpy as np
import torch

heater_valve = 0
heater_envelope = 0
blinds = 0
blinds_blocked = False


def predict_temperature_for_prediction(room, constants, T_r, T_a, solar_watt, heating_setpoint,
                                       cooling_setpoint, lux, wind, heating_effects, solar_effects):
    a_a, a_s, a_h, a_v, a_o = constants

    T = np.zeros_like(T_r)
    T[0] = T_r[0]
    for i in range(1, len(T_r)):
        blinds_control_py(solar_watt[i], wind[i])
        S_t = solar_effect(room, solar_watt[i])
        E_h = heater_effect(room, heating_setpoint[i], T[i - 1])
        O = max(occupancy_effect(lux[i]) - S_t, 0)
        heating_effects[i - 1] = E_h
        solar_effects[i - 1] = S_t

        if i % 240 == 0:
            T[i] = T_r[i]
        else:
            T[i] = T[i - 1] + derivative_function(T_a[i], T_r[i - 1], a_a, E_h, a_h, a_v, S_t, a_s, O, a_o)
    return T

def predict_temperature_for_training(room, constants, T_r, T_a, S_t, heating_setpoint, cooling_setpoint, O):
    a_a, a_s, a_h, a_v, a_o = constants

    T = np.zeros_like(T_r)
    T[0] = T_r[0]
    for i in range(1, len(T_r)):
        E_h = heater_effect(room, heating_setpoint[i], T[i - 1])
        if i % 240 == 0:
            T[i] = T_r[i]
        else:
            T[i] = T[i - 1] + derivative_function(T_a[i], T_r[i - 1], a_a, E_h, a_h, a_v, S_t, a_s, O, a_o)
    return T


"""
@params T_a: Is ambient temperature
@params T_r: Is room temperature
@params a_a: Is the ambient temperature constant
@params E_h: Is the heating effect
@params a_h: Is the heating effect constant
@params a_v: Is the ventilation effect constant
@params S_t: Is the solar effect
@params a_s: Is the solar effect constant
@params O: Is the occupancy effect
@params a_o: Is the occupancy effect constant
The derivative function is defined as follows:
"""
def derivative_function(T_a, T_r, a_a, E_h, a_h, a_v, S_t, a_s, O, a_o):
    return ((T_a - T_r) * a_a +
            S_t * a_s +
            E_h * a_h +
            (T_a - T_r) * a_v +
            O * a_o)


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
'''
@params df_watt: list of solar_watt
@returns: solar effect
Calculates the solar_watt from the sun based on the g-value and window area
'''
def solar_effect(room, df_watt):
    global blinds
    sun_block = 0
    if blinds == 1:
        sun_block = 0.2
    else:
        sun_block = 1
    G = 0.45
    return df_watt * G * room["window_size"] * sun_block


'''
@params heating_setpoint: list of heating setpoints
@params current_temperature: current temperature in the room
@returns: heater effect
Function for calculating the heater's effect on the room
If the current temperature is below the heating setpoint, the heater is on else off
'''
def heater_effect(room, heating_setpoint, current_temperature):
    max_heat_stored = room["heater_effect"]
    charge_effect = 0.02
    decay_effect = 0.02

    global heater_envelope
    # In your update step
    if current_temperature <= heating_setpoint:
        heater_envelope = min(heater_envelope + charge_effect * max_heat_stored, max_heat_stored)
    else:
        # Exponential decay
        heater_envelope *= math.exp(-decay_effect)

    return heater_envelope


def occupancy_effect(lux):
    lpp = 300
    e_p = 100
    return lux / lpp * e_p #lpp is lux per person, e_p is wattage per person











def heater_effect_torch(heating_setpoint, room_temp, max_heat, charge=0.02, decay=0.02):
    envelope = torch.zeros_like(room_temp)
    decay_tensor = torch.tensor(decay, dtype=torch.float32, device=envelope.device)
    for i in range(1, len(room_temp)):
        is_on = room_temp[i - 1] <= heating_setpoint[i - 1]
        if is_on:
            envelope[i] = torch.clamp(envelope[i - 1] + charge * max_heat, max=max_heat)
        else:
            envelope[i] = envelope[i - 1] * torch.exp(-decay_tensor)
    return envelope


class RoomTemperatureODE(torch.nn.Module):
    def __init__(self, room, inputs, constants):
        super().__init__()
        self.room = room
        self.inputs = inputs  # tuple of external signals
        self.constants = constants  # [a_a, a_s, a_h, a_v, a_o]

    def forward(self, t, T_r):
        idx = int(t.item())  # Assume integer timesteps (0, 1, 2, ...)
        T_a, S_t, E_h, O = self.inputs

        a_a, a_s, a_h, a_v, a_o = self.constants

        dTdt = ((T_a[idx] - T_r) * a_a +
                S_t[idx] * a_s +
                E_h[idx] * a_h +
                (T_a[idx] - T_r) * a_v +
                O[idx] * a_o)

        return dTdt
