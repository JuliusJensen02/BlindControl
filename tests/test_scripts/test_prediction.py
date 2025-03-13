import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from scripts.prediction import predict_for_date # Import the function to test
from scripts.data_processing import convert_csv_to_df
from scripts.derivative_functions import predict_temperature
from scripts.plot import plot_df

# Mock constants for the prediction
constants_mock = {
    'constant_1': 1.5,
    'constant_2': 2.3,
    'constant_3': 3.1,
    'constant_4': 4.2,
}

@pytest.fixture
def sample_df():
    # Creating a sample DataFrame that simulates the expected format after querying data
    data = {
        "time": ["2025-03-01 12:00", "2025-03-01 12:05", "2025-03-01 12:10"],
        "room_temp": [22.5, 23.0, 23.5],
        "ambient_temp": [21.0, 21.2, 21.5],
        "solar_watt": [300, 320, 310],
        "heating_setpoint": [22.0, 22.0, 22.0],
        "cooling_setpoint": [24.0, 24.0, 24.0]
    }
    return pd.DataFrame(data)

@patch('scripts.data_processing.convert_csv_to_df')  # Mocking convert_csv_to_df function
@patch('scripts.derivative_functions.predict_temperature')  # Mocking predict_temperature function
@patch('scripts.plot.plot_df')  # Mocking plot_df function
def test_predict_for_date(mock_plot, mock_predict_temp, mock_convert_csv, sample_df):
    # Mock convert_csv_to_df to return our sample dataframe
    mock_convert_csv.return_value = sample_df

    # Mock predict_temperature to return a list of predicted values
    mock_predict_temp.return_value = [22.7, 23.2, 23.6]  # Simulating predictions

    # Test when plot=True
    predict_for_date("2025-03-01T00:00:00Z", constants_mock, plot=False)

    # Ensure convert_csv_to_df was called
    mock_convert_csv.assert_called_once


    # Test when plot=False (just return the DataFrame)
    result_df = predict_for_date("2025-03-01T00:00:00Z", constants_mock, plot=False)

    # Ensure it returns the DataFrame with the predicted temperature
    assert 'temp_predictions' in result_df.columns
