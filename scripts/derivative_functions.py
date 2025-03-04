import numpy as np
from scipy.integrate import solve_ivp

'''
Function for predicting the temperature for the training functions
'''
def predict_temperature(constants, room_temp, ambient_temp, watt, opening_signal):
    alpha_a, alpha_s, alpha_r, alpha_v = constants
    t_span = (0, len(room_temp) - 1)  # Time range
    t_eval = np.arange(len(room_temp))  # Discrete evaluation points

    # Solve the ODE
    sol = solve_ivp(temp_derivative, t_span, [room_temp[0]], t_eval=t_eval, args=(alpha_a, alpha_s, alpha_r, alpha_v, ambient_temp, watt, opening_signal))
    return sol.y[0]  # Return the temperature predictions


'''
Function that the solve_ivp uses to calculate the derivative temperature function 
'''
def temp_derivative(t, T, alpha_a, alpha_s, alpha_r, alpha_v, ambient_temp, watt, opening_signal):
    t = int(t)
    if t >= len(ambient_temp):
        t = len(ambient_temp) - 1
    return (ambient_temp[t] - T) * alpha_a + solar_effect(watt[t]) * alpha_s + heater_effect(opening_signal[t]) * alpha_r + alpha_v


'''
Calculates the watt from the sun based on the g-value and window area
'''
def solar_effect(df_watt):
    G = 0.7
    mean_window_area_group = 4.25
    return df_watt * G * mean_window_area_group


'''
Calculates the heater's effect on the room
'''
def heater_effect(opening_signal):
    return (opening_signal / 100) * 372


'''
Function for calculating the ventilation's effect on the room
'''
def ventilation_effect(something):
    return 1