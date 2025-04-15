import math
import torch
import torchdiffeq

blinds = 0
blinds_blocked = False

"""
The current control for the solar blinds at BUILD implemented in Python.
Args:
    solar_watt: the amount of solar watt at a given time.
    wind: the amount of wind at a given time.
"""
def blinds_control_py(solar_watt: float, wind: float) -> None:
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

"""
Function that calculates the solar effect based on the blinds, the solar watt,
the g-value of the window and the window size.
Args:
    room: the room id.
    df_watt: the amount of solar watt at a given time.
Returns:
    The solar effect based on the blinds, the solar watt, the g-value and the window size.
"""
def solar_effect(room: dict, df_watt: float) -> float:
    global blinds
    sun_block = 0
    if blinds == 1:
        sun_block = 0.2
    else:
        sun_block = 1
    G = 0.45
    return df_watt * G * room["window_size"] * sun_block


def occupancy_effect(lux):
    lpp = 300
    e_p = 100
    return lux / lpp * e_p #lpp is lux per person, e_p is wattage per person
