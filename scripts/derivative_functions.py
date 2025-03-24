import numpy as np
from sympy import false

heater_valve = 0
blinds = 0
blinds_blocked = False
'''
@params constants: list of constants
@params room_temp: list of room temperatures
@params ambient_temp: list of ambient temperatures
@params solar_watt: list of solar_watt
@params heating_setpoint: list of heating setpoints
@params cooling_setpoint: list of cooling setpoints
@returns sol.y[0]: list of temperature predictions
Function for predicting the temperature for the training functions
'''
def predict_temperature(room, constants, T_r, T_a, solar_watt, heating_setpoint, cooling_setpoint, lux, wind, heating_effects = None, solar_effects = None):
    a_a, a_s, a_h, a_v, a_o = constants

    T = np.zeros_like(T_r)
    T[0] = T_r[0]
    for i in range(1, len(T_r)):
        S_t = solar_effect(room, solar_watt[i])
        E_h = heater_effect(room, heating_setpoint[i], T[i-1])
        O = max(occupancy_effect(lux[i]) - S_t, 0)
        if heating_effects is not None:
            heating_effects[i-1] = E_h
            solar_effects[i-1] = S_t
        for j in range(15):
            T[i] = T[i - 1] + (1/15) * derivative_function(T_a[i], T_r[i - 1], a_a, E_h, a_h, a_v, S_t, a_s, O, a_o)
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
    global heater_valve
    if current_temperature <= heating_setpoint:
        heater_valve += 0.25
        if heater_valve > 1:
            heater_valve = 1

    elif current_temperature > heating_setpoint:
        heater_valve -= 0.25
        if heater_valve < 0:
            heater_valve = 0

    return room["heater_effect"] * heater_valve


def occupancy_effect(lux):
    lpp = 300
    e_p = 100
    return lux / lpp * e_p #lpp is lux per person, e_p is wattage per person