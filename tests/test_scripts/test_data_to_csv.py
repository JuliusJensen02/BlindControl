import pytest
import os
import csv
from datetime import datetime
from unittest.mock import patch, MagicMock
from scripts.data_to_csv import cache_constants, hour_rounder, query_data, reset_csv
from test_data_processing import sample_data
from influxdb_client.client.query_api import QueryApi


def test_round_up():
    dt = datetime(2024, 3, 4, 15, 45)  # 45 minutes, should round up to 16:00
    rounded = hour_rounder(dt)
    assert rounded == datetime(2024, 3, 4, 16, 0)

def test_round_down():
    dt = datetime(2024, 3, 4, 15, 15)  # 15 minutes, should round down to 15:00
    rounded = hour_rounder(dt)
    assert rounded == datetime(2024, 3, 4, 15, 0)

def test_exact_half():
    dt = datetime(2024, 3, 4, 15, 30)  # Should round to 16:00
    rounded = hour_rounder(dt)
    assert rounded == datetime(2024, 3, 4, 16, 0)

@patch('influxdb_client.InfluxDBClient.query_api')
@patch('scripts.data_to_csv.get_temp')
def test_query_data(mock_get_temp, mock_query_api):
    # Mock the InfluxDB query_api correctly
    mock_query_api = MagicMock(spec=QueryApi)
    
    # Mock the response from InfluxDB
    mock_query_api.query.return_value = [
        MagicMock(values={"solar_watt": 5.0, "room_temp": 22.5, "heating_setpoint": 20.0, "cooling_setpoint": 24.0, "_time": datetime(2024, 12, 27, 17, 22)}),       
        MagicMock(values={"solar_watt": 4.5, "room_temp": 22.3, "heating_setpoint": 20.5, "cooling_setpoint": 24.5, "_time": datetime(2024, 12, 27, 17, 37)})        
    ]

    # Mock the response from the DMI API
    mock_get_temp.return_value = {
        "2024-12-27T17:00:00": 5.0,
        "2024-12-27T18:00:00": 4.8
    }

    # Run the function
    query_data(input_from="2024-12-27T00:00:00Z", days=1)


# Test for resetting CSV
def test_reset_csv(sample_data):
    # File path to test data
    file_path = 'tests/test_data/test_data.csv'
    
    # Ensure the file exists and is empty before the test
    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = ['time', 'solar_watt', 'room_temp', 'ambient_temp', 'heating_setpoint', 'cooling_setpoint']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()  # Write header to the CSV file

    # Write sample data to the CSV file
    with open(file_path, 'a', newline='') as csvfile:
        fieldnames = ['time', 'solar_watt', 'room_temp', 'ambient_temp', 'heating_setpoint', 'cooling_setpoint']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerows(sample_data.to_dict(orient='records'))

    # Now reset the CSV file
    reset_csv(file_path)

    # Check if the file is empty after reset
    with open(file_path, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 1  # It should only contain the header

def test_cache_constants():
    # Call the function to cache constants
    cache_constants(1.2, 3.4, 5.6, 7.8, "2024-12-27T00:00:00Z", 1, 0.5, 'tests/test_data/test_constants_cache.csv')
    
    # Check if the constants are written correctly to the file
    with open('tests/test_data/test_constants_cache.csv', 'r') as csvfile:
        lines = csvfile.readlines()
        # Check if the first line is the header
        assert lines[0].startswith("alpha_a")
        # Check if the second line contains the correct values
        assert "1.2" in lines[1]
        assert "3.4" in lines[1]
        assert "5.6" in lines[1]
        assert "7.8" in lines[1]
        assert "2024-12-27T00:00:00Z" in lines[1]