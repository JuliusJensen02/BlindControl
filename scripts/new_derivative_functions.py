import math
import torch
import torchdiffeq
import numpy as np

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


"""
This function calculates the energy effect of the occupancy in the room.
It takes into account the setpoints of the heater and cooler, the time of day, and the occupancy probability distribution of the room.
Args: 
    heating_setpoint: the setpoint of the heater
    cooling_setpoint: the setpoint of the cooler
    time: the time in minutes since midnight
    room: the room object containing the group and prob_dist attributes
Returns: 
    the energy effect of the occupancy in the room
"""
def occupancy_effect(heating_setpoint: float, cooling_setpoint: float, time: int, room: dict) -> float:
    # Energy effect of the occupancy in the room dependent on office or grouproom. Office is more heat because of pcs and other devices.
    energy_people = 150 if room["group"] else 250 
    occupancy = 0

    if cooling_setpoint - heating_setpoint == 1 :

        if (time < 480):
            occupancy = np.random.choice(room["values"], p=room["prob_dist"][0]) # Occupancy probability distribution from 0 to 8 hours
        elif (time < 720):
            occupancy = np.random.choice(room["values"], p=room["prob_dist"][1]) # Occupancy probability distribution from 8 to 12 hours
        elif (time < 960):
            occupancy = np.random.choice(room["values"], p=room["prob_dist"][2]) # Occupancy probability distribution from 12 to 16 hours
        else:
            occupancy = np.random.choice(room["values"], p=room["prob_dist"][3]) # Occupancy probability distribution from 16 to 24 hours
        
        return occupancy * energy_people
    else:
        return 0