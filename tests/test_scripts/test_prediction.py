import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from scripts.prediction import predict_for_date # Import the function to test

# Mock constants for the prediction
constants_mock = {
    'constant_1': 1.5,
    'constant_2': 2.3
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

@patch('scripts.prediction.reset_csv')  # Mocking reset_csv function
@patch('scripts.prediction.query_data')  # Mocking query_data function
@patch('scripts.prediction.convert_csv_to_df')  # Mocking convert_csv_to_df function
@patch('scripts.prediction.predict_temperature')  # Mocking predict_temperature function
@patch('scripts.prediction.plot_df')  # Mocking plot_df function
def test_predict_for_date(mock_plot, mock_predict_temp, mock_convert_csv, mock_query_data, mock_reset_csv, sample_df):
    # Mock reset_csv and query_data to avoid actually manipulating files or querying data
    mock_reset_csv.return_value = None
    mock_query_data.return_value = None

    # Mock convert_csv_to_df to return our sample dataframe
    mock_convert_csv.return_value = sample_df

    # Mock predict_temperature to return a list of predicted values
    mock_predict_temp.return_value = [22.7, 23.2, 23.6]  # Simulating predictions

    # Test when plot=True
    predict_for_date("2025-03-01", constants_mock, plot=True)

    # Ensure reset_csv and query_data were called
    mock_reset_csv.assert_called_once()
    mock_query_data.assert_called_once_with("2025-03-01", 1)

    # Ensure convert_csv_to_df was called
    mock_convert_csv.assert_called_once_with("data/data.csv")

    # Convert the numpy arrays to lists before the comparison
    room_temp = sample_df["room_temp"].values
    ambient_temp = sample_df["ambient_temp"].values
    solar_watt = sample_df["solar_watt"].values
    heating_setpoint = sample_df["heating_setpoint"].values
    cooling_setpoint = sample_df["cooling_setpoint"].values

    # Ensure plot_df was called
    mock_plot.assert_called_once_with(sample_df)

    # Test when plot=False (just return the DataFrame)
    result_df = predict_for_date("2025-03-01", constants_mock, plot=False)

    # Ensure it returns the DataFrame with the predicted temperature
    assert 'temp_predictions' in result_df.columns
    assert result_df['temp_predictions'].equals(pd.Series([22.7, 23.2, 23.6]))