import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
import numpy as np
from io import StringIO
from datetime import timedelta
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




@patch('scripts.greybox_fitting.reset_csv')
@patch('scripts.greybox_fitting.query_data')
@patch('scripts.greybox_fitting.convert_csv_to_df')
@patch('scripts.greybox_fitting.remove_outliers')
@patch('scripts.greybox_fitting.smooth')
@patch('scripts.greybox_fitting.use_best_optimization_method')
@patch('scripts.greybox_fitting.cache_constants')
def test_train_for_time_frame(
    mock_cache_constants, mock_use_best_optimization_method, mock_smooth,
    mock_remove_outliers, mock_convert_csv_to_df, mock_query_data, mock_reset_csv, sample_data
):
    # Mock helper functions
    mock_reset_csv.return_value = None
    mock_query_data.return_value = None
    mock_convert_csv_to_df.return_value = sample_data
    mock_remove_outliers.return_value = sample_data
    mock_smooth.return_value = sample_data
    mock_use_best_optimization_method.return_value = MagicMock(x=np.array([0.1, 0.2, 0.3, 0.4]), fun=0.05)
    mock_cache_constants.return_value = None

    start_time = "2024-12-27T00:00:00Z"
    days = 1

    # Call the function
    train_for_time_frame(start_time, days)

    # Verify calls
    mock_reset_csv.assert_called_once()
    mock_query_data.assert_called_once_with(start_time, days)
    mock_convert_csv_to_df.assert_called_once_with("data/data.csv")
    mock_remove_outliers.assert_called_once()
    mock_smooth.assert_called_once()

    # Validate optimization call with correct arguments
    actual_args, _ = mock_use_best_optimization_method.call_args
    expected_args = (
        np.array([0.01, 0.001, 0.01, 0.01]),
        [(0, 1), (0, 1), (0, 1), (0, 1)],
        sample_data["room_temp"].values,
        sample_data["ambient_temp"].values,
        sample_data["solar_watt"].values,
        sample_data["heating_setpoint"].values,
        sample_data["cooling_setpoint"].values,
        [None]
    )

    for actual, expected in zip(actual_args[:7], expected_args[:7]):
        assert np.array_equal(actual, expected), f"Mismatch in optimization argument: {actual} != {expected}"
    assert actual_args[7] == expected_args[7], "Mismatch in best method argument"

    # Validate caching call
    mock_cache_constants.assert_called_once_with(0.1, 0.2, 0.3, 0.4, start_time, days, 0.05)


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
    result = use_best_optimization_method(initial_guess, bounds, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint, best_method)

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
