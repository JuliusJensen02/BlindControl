import pytest
import numpy as np
from scripts.derivative_functions import predict_temperature, solar_effect, heater_effect
from test_data_processing import sample_data


def test_solar_effect():
    assert solar_effect(0) == 0  # No solar input
    assert solar_effect(1000) == pytest.approx((0.7 * 4.25 * 1000), rel=1e-5)


def test_heater_effect():
    heating_setpoint = 23.0
    current_temperature = 22.9  # Below heating_setpoint

    result = heater_effect(heating_setpoint, current_temperature)

    assert result == 372 * 0.25

    heating_setpoint = 23.0
    current_temperature = 22.9  # Below heating_setpoint

    result = heater_effect(heating_setpoint, current_temperature)

    assert result == 372 * 0.5 


# Test predict_temperature
@pytest.mark.parametrize("constants", [(0.1, 0.2, 0.3, 0.4)])
def test_predict_temperature(sample_data, constants):
    room_temp = sample_data['room_temp'].tolist()
    ambient_temp = sample_data['ambient_temp'].tolist()
    solar_watt = sample_data['solar_watt'].tolist()
    heating_setpoint = sample_data['heating_setpoint'].tolist()
    
    result = predict_temperature(constants, room_temp, ambient_temp, solar_watt, heating_setpoint)
    assert isinstance(result, np.ndarray)
    assert len(result) == len(room_temp)
    assert result[0] == room_temp[0]
