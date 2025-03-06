import numpy as np

heater_turned_on_percentage = 0
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
def predict_temperature(constants, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint, heating_effects = None, solar_effects = None):
    alpha_a, alpha_s, alpha_r, alpha_v = constants

    T = np.zeros_like(room_temp)
    T[0] = room_temp[0]
    dt = 0.25
    for i in range(1, len(room_temp)):
        S_t = solar_effect(solar_watt[i])
        H_t = heater_effect(heating_setpoint[i], T[i-1])
        if heating_effects is not None:
            solar_effects[i-1] = S_t
            heating_effects[i-1] = H_t
        dT = ((ambient_temp[i] - T[i - 1]) * alpha_a + S_t * alpha_s + H_t * alpha_r + alpha_v)
        T[i] = T[i - 1] + dT
    return T
    # Solve the ODE
    #sol = solve_ivp(temp_derivative, t_span, [room_temp[0]], t_eval=t_eval, method='LSODA',
    #                args=(alpha_a, alpha_s, alpha_r, alpha_v, ambient_temp, solar_watt, heating_setpoint))
    #return sol.y[0]  # Return the temperature predictions




'''
@params t: time 
@params T: temperature in the room
@params alpha_a: alpha_a constant for ambient temperature
@params alpha_s: alpha_s constant for solar effect
@params alpha_r: alpha_r constant for heater effect
@params alpha_v: alpha_v constant for ventilation effect
@params ambient_temp: list of ambient temperatures
@params solar_watt: list of solar_watt
@params heating_setpoint: list of heating setpoints
@params cooling_setpoint: list of cooling setpoints
@params heating_bool: boolean for heating
@returns: temperature derivative
Function that the solve_ivp uses to calculate the derivative temperature function for the room
'''
def temp_derivative(t, T, alpha_a, alpha_s, alpha_r, alpha_v, ambient_temp, solar_watt, heating_setpoint):
    t = min(int(t), len(ambient_temp) - 1)
    ambient_temp_effect = (ambient_temp[t] - T) * alpha_a
    solar_watt_effect = solar_effect(solar_watt[t]) * alpha_s
    heating_effect = (372 if T[0] <= heating_setpoint[t] else 0) * alpha_r
    ventilating_effect = alpha_v

    return ambient_temp_effect + solar_watt_effect + heating_effect + ventilating_effect


'''
@params df_watt: list of solar_watt
@returns: solar effect
Calculates the solar_watt from the sun based on the g-value and window area
'''
def solar_effect(df_watt):
    G = 0.7
    mean_window_area_group = 4.25
    return df_watt * G * mean_window_area_group #The G value is an estimation TODO: Change to a more accurate value


'''
@params heating_setpoint: list of heating setpoints
@params cooling_setpoint: list of cooling setpoints
@params current_temperature: current temperature in the room
@params heating_bool: boolean for heating
@returns: heater effect
Function for calculating the heater's effect on the room
If the current temperature is below the heating setpoint, the heater is on
If the current temperature is above the cooling setpoint, the heater is off
'''
def heater_effect(heating_setpoint, current_temperature):
    global heater_turned_on_percentage
    if current_temperature <= heating_setpoint:
        heater_turned_on_percentage += 0.25
        if heater_turned_on_percentage > 1:
            heater_turned_on_percentage = 1

    elif current_temperature > heating_setpoint:
        heater_turned_on_percentage -= 0.25
        if heater_turned_on_percentage < 0:
            heater_turned_on_percentage = 0

    return 372 * heater_turned_on_percentage


'''
TODO: Implement the ventilation effect
Function for calculating the ventilation's effect on the room
'''
def ventilation_effect(something):
    return 1