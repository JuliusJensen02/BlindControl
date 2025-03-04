import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
import numpy as np
from io import StringIO
from datetime import timedelta
from scripts.greybox_fitting import get_constants, train_for_time_frame, use_best_optimization_method, mean_squared_error
from test_data_processing import sample_data

@patch('os.path.getsize')  # Mocking os.path.getsize
@patch('pandas.read_csv')  # Mocking pd.read_csv
@patch('scripts.greybox_fitting.train_for_time_frame')  # Mocking train_for_time_frame
def test_get_constants(mock_train, mock_read_csv, mock_getsize):
    # Mocking os.path.getsize to simulate a non-empty cache file
    mock_getsize.return_value = 100

    # Mock the dataframe returned by pd.read_csv
    mock_df = MagicMock()
    mock_df['alpha_a'] = 0.5
    mock_df['alpha_s'] = 0.6
    mock_df['alpha_r'] = 0.7
    mock_df['alpha_v'] = 0.8
    mock_df['start_time'] = ['2025-01-01T00:00:00Z']
    mock_df['days'] = [1]
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

@patch('os.path.getsize')
@patch('pandas.read_csv')
@patch('scripts.greybox_fitting.train_for_time_frame')
def test_get_constants_retrain(mock_train, mock_read_csv, mock_getsize):
    # Simulate an empty cache file, which would trigger retraining
    mock_getsize.return_value = 0

    # Mock train_for_time_frame to not perform any operations
    mock_train.return_value = None

    # Mock the dataframe returned by pd.read_csv
    mock_df = MagicMock()
    mock_df['alpha_a'] = [0.5]
    mock_df['alpha_s'] = [0.6]
    mock_df['alpha_r'] = [0.7]
    mock_df['alpha_v'] = [0.8]
    mock_df['start_time'] = ['2025-01-01T00:00:00Z']
    mock_df['days'] = [1]
    mock_read_csv.return_value = mock_df
    
    # Call the function
    constants = get_constants(start_time="2025-01-01T00:00:00Z", days=1, retrain=True)

    # Assertions
    assert constants == {'alpha_a': 0.5, 'alpha_s': 0.6, 'alpha_r': 0.7, 'alpha_v': 0.8}
    mock_train.assert_called_once()  # Ensure train_for_time_frame was called


@patch('scripts.data_to_csv.reset_csv')
@patch('scripts.data_to_csv.query_data')
@patch('scripts.data_processing.convert_csv_to_df')
@patch('scripts.data_processing.remove_outliers')
@patch('scripts.data_processing.smooth')
@patch('scripts.greybox_fitting.use_best_optimization_method')
@patch('scripts.data_to_csv.cache_constants')
def test_train_for_time_frame(mock_cache_constants, mock_use_best_optimization_method, mock_smooth, mock_remove_outliers, mock_convert_csv_to_df, mock_query_data, mock_reset_csv, sample_data):
    # Mocking the helper functions
    mock_reset_csv.return_value = None
    mock_query_data.return_value = None
    mock_convert_csv_to_df.return_value = sample_data  # Mocking the conversion function to return the sample data
    mock_remove_outliers.return_value = sample_data  # Mocking the remove_outliers function
    mock_smooth.return_value = sample_data  # Mocking the smoothing function
    mock_use_best_optimization_method.return_value = MagicMock(x=np.array([0.1, 0.2, 0.3, 0.4]), fun=0.05)  # Mocking the optimization result
    mock_cache_constants.return_value = None  # No return for caching function

    start_time = "2024-12-27T09:00:00Z"
    days = 2  # At least 1 day

    # Call the method to train the model
    train_for_time_frame(start_time, days)

    # Assertions to ensure the methods were called correctly
    mock_reset_csv.assert_called_once()
    mock_query_data.assert_called_once_with(start_time, 1)
    mock_convert_csv_to_df.assert_called_once_with("data/data.csv")
    mock_remove_outliers.assert_called_once()
    mock_smooth.assert_called_once()
    mock_use_best_optimization_method.assert_called_once_with(
        np.array([0.01, 0.001, 0.01, 0.01]), [(0, 1), (0, 1), (0, 1), (0, 1)], sample_data["room_temp"].values,
        sample_data["ambient_temp"].values, sample_data["solar_watt"].values, sample_data["heating_setpoint"].values,
        sample_data["cooling_setpoint"].values, [None]
    )
    mock_cache_constants.assert_called_once_with(0.1, 0.2, 0.3, 0.4, start_time, days, 0.05)


@patch('scipy.optimize.minimize')
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
    assert result.fun == 0.1
    assert result.x == [0.1, 0.2, 0.3, 0.4]
    assert best_method[0] is not None  # Ensure the method is set
    mock_minimize.assert_called_once_with(
        'mean_squared_error', initial_guess, method='Powell', bounds=bounds,
        args=(room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint)
    )

@patch('scripts.derivative_functions.predict_temperature')
def test_mean_squared_error(mock_predict):
    # Mock the predicted temperatures
    mock_predict.return_value = np.array([20, 21, 22])

    # Define inputs
    constants = [0.1, 0.2, 0.3, 0.4]
    room_temp = np.array([20, 21, 22])
    ambient_temp = np.array([15, 16, 17])
    solar_watt = np.array([100, 150, 200])
    heating_setpoint = np.array([18, 19, 20])
    cooling_setpoint = np.array([22, 21, 20])

    # Call the function
    error = mean_squared_error(constants, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint)

    # Assertions
    assert error == 0  # Since mock_predict returns the exact room_temp values
    mock_predict.assert_called_once_with(constants, room_temp, ambient_temp, solar_watt, heating_setpoint, cooling_setpoint)