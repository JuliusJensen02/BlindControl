import pytest
import numpy as np
from scipy.integrate import solve_ivp
from scripts.derivative_functions import predict_temperature, temp_derivative, solar_effect, heater_effect
from test_data_processing import sample_data


def test_solar_effect():
    assert solar_effect(0) == 0  # No solar input
    assert solar_effect(1000) == pytest.approx((0.7 * 4.25 * 1000), rel=1e-5)


def test_heater_effect():
    heating_setpoint = 23.0
    cooling_setpoint = 25.0
    current_temperature = 22.9  # Below heating_setpoint
    heating_bool = [False]  # Initially False

    result = heater_effect(heating_setpoint, cooling_setpoint, current_temperature, heating_bool)

    assert result == 372  # Heater should turn ON, returning 372
    assert heating_bool[0] is True  # heating_bool should be updated


# Test temp_derivative
@pytest.mark.parametrize("t, T, expected", [(0, 22.0, -0.5), (1, 22.5, -0.4)])
def test_temp_derivative(sample_data, t, T, expected):
    alpha_a, alpha_s, alpha_r, alpha_v = 0.1, 0.2, 0.3, 0.4
    ambient_temp = sample_data['ambient_temp'].tolist()
    solar_watt = sample_data['solar_watt'].tolist()
    heating_setpoint = sample_data['heating_setpoint'].tolist()
    cooling_setpoint = sample_data['cooling_setpoint'].tolist() 
    heating_bool = [False]
    
    result = temp_derivative(t, T, alpha_a, alpha_s, alpha_r, alpha_v, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint, heating_bool)
    assert isinstance(result, float)


# Test predict_temperature
@pytest.mark.parametrize("constants", [(0.1, 0.2, 0.3, 0.4)])
def test_predict_temperature(sample_data, constants):
    room_temp = sample_data['room_temp'].tolist()
    ambient_temp = sample_data['ambient_temp'].tolist()
    solar_watt = sample_data['solar_watt'].tolist()
    heating_setpoint = sample_data['heating_setpoint'].tolist()
    cooling_setpoint = sample_data['cooling_setpoint'].tolist()
    
    result = predict_temperature(constants, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint)
    assert isinstance(result, np.ndarray)
    assert len(result) == len(room_temp)
    assert result[0] == room_temp[0]
