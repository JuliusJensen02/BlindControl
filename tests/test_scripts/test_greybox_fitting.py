import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
import numpy as np
from io import StringIO
from datetime import datetime, timedelta
from scripts.greybox_fitting import get_constants, train_for_time_frame, use_best_optimization_method, mean_squared_error
from scripts.data_processing import convert_csv_to_df, remove_outliers, smooth
from scripts.data_to_csv import reset_csv, query_data, cache_constants
from scripts.derivative_functions import predict_temperature
from test_data_processing import sample_data

@patch('os.path.getsize')  # Mocking os.path.getsize
@patch('pandas.read_csv')  # Mocking pd.read_csv
@patch('scripts.greybox_fitting.train_for_time_frame')  # Mocking train_for_time_frame
def test_get_constants(mock_train, mock_read_csv, mock_getsize):
    # Mocking os.path.getsize to simulate a non-empty cache file
    mock_getsize.return_value = 100

    mock_df = pd.DataFrame({
        'alpha_a': [0.5],
        'alpha_s': [0.6],
        'alpha_r': [0.7],
        'alpha_v': [0.8],
        'start_time': ['2025-01-01T00:00:00Z'],
        'days': [1]
    })
    mock_read_csv.return_value = mock_df
    
    # Call the function
    constants = get_constants(start_time="2025-01-01T00:00:00Z", days=1, retrain=False, path = "tests/test_data/test_data.csv")

    # Assertions
    assert constants['alpha_a'] == pytest.approx(0.5)
    assert constants['alpha_s'] == pytest.approx(0.6)
    assert constants['alpha_r'] == pytest.approx(0.7)
    assert constants['alpha_v'] == pytest.approx(0.8)
    mock_train.assert_not_called()  # Ensure train_for_time_frame was not called
    mock_getsize.assert_called_once_with("tests/test_data/test_data.csv")


@pytest.fixture
def mock_data():
    # Example data to return from train_for_day
    return [1, 1, 1, 1, 1]  # alpha_a, alpha_s, alpha_r, alpha_v, error


@patch('scripts.greybox_fitting.cache_constants')  # Mock cache_constants function
@patch('scripts.greybox_fitting.train_for_day')  # Mock train_for_day function
@patch('multiprocessing.Pool')  # Mock multiprocessing.Pool
def test_train_for_time_frame(mock_pool, mock_train_for_day, mock_cache_constants, mock_data):
    # Mock the behavior of train_for_day
    mock_train_for_day.return_value = mock_data  # Mock return values of train_for_day

    # Mock the multiprocessing Pool
    mock_pool.return_value.__enter__.return_value.starmap.return_value = [mock_data] * 5  # Simulating 5 days of data


    # Call the function
    start_time = "2025-01-01T00:00:00Z"
    days = 5
    train_for_time_frame(start_time, days)

    # Assert that train_for_day was called the correct number of times
    assert mock_train_for_day.call_count == days

    # Assert that cache_constants is called with the correct parameters
    expected_alpha_a = sum([d[0] for d in [mock_data] * days]) / days
    expected_alpha_s = sum([d[1] for d in [mock_data] * days]) / days
    expected_alpha_r = sum([d[2] for d in [mock_data] * days]) / days
    expected_alpha_v = sum([d[3] for d in [mock_data] * days]) / days
    expected_error = sum([d[4] for d in [mock_data] * days]) / days

    mock_cache_constants.assert_called_once_with(expected_alpha_a, expected_alpha_s, expected_alpha_r,
                                                 expected_alpha_v, start_time, days, expected_error)

@patch('scripts.greybox_fitting.minimize')
def test_use_best_optimization_method(mock_minimize):
    # Mock the result of the minimize function
    mock_result = MagicMock()
    mock_result.fun = 0.1
    mock_result.x = [0.1, 0.2, 0.3, 0.4]
    mock_minimize.return_value = mock_result

    # Define inputs
    initial_guess = [0.01, 0.02, 0.03, 0.04]
    bounds = [(0, 1), (0, 1), (0, 1), (0, 1)]
    room_temp = np.array([20, 21, 22])
    ambient_temp = np.array([15, 16, 17])
    solar_watt = np.array([100, 150, 200])
    heating_setpoint = np.array([18, 19, 20])
    cooling_setpoint = np.array([22, 21, 20])
    best_method = [None]

    # Call the function
    result = use_best_optimization_method(room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint, best_method)

    # Assertions
    assert result.fun == pytest.approx(0.1)
    assert result.x == [0.1, 0.2, 0.3, 0.4]
    assert best_method[0] is not None  # Ensure the method is set
    assert mock_minimize.call_count >= 1  # Ensure the function was called at least once


@patch('scripts.greybox_fitting.predict_temperature')
def test_mean_squared_error(mock_predict):
    # Mock the predicted temperatures
    mock_predict.return_value = np.array([20, 21, 22])

    # Define inputs
    room_temp = np.array([20, 21, 22])
    constants = [0.1, 0.2, 0.3, 0.4]
    ambient_temp = np.array([15, 16, 17])
    solar_watt = np.array([100, 150, 200])
    heating_setpoint = np.array([18, 19, 20])
    cooling_setpoint = np.array([22, 21, 20])

    # Call the function
    error = mean_squared_error(constants, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint)

    # Assertions
    mock_predict.assert_called_once_with(constants, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint)
    assert error == pytest.approx(0, abs=1e-6)  # Allow for floating-point precision issues
