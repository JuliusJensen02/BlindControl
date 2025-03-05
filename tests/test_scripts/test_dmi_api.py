import pytest
from unittest.mock import patch, MagicMock
import json
import requests

# Assuming the function is in a file called 'temperature.py'
from scripts.dmi_api import get_temp

# Test case for successful response with data
@patch('requests.get')  # Mocking the requests.get method
def test_get_temp(mock_get):
    # Sample mocked response
    mocked_response = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "from": "2024-11-23T00:00:00Z",
                    "value": 10.5
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "from": "2024-11-23T01:00:00Z",
                    "value": 11.0
                }
            }
        ]
    }
    
    # Create a MagicMock object for the mocked response
    mock_response = MagicMock()
    mock_response.text = json.dumps(mocked_response)
    mock_get.return_value = mock_response  # Set the return value of requests.get to our mock_response

    # Call the function
    temp_map = get_temp("2024-11-23T00:00:00Z", "2024-11-23T02:00:00Z")

    # Assertions
    assert len(temp_map) == 2  # Check that we have 2 items in the result
    assert temp_map["2024-11-23T00:00:00Z"] == 10.5  # Check temperature for the first time
    assert temp_map["2024-11-23T01:00:00Z"] == 11.0  # Check temperature for the second time

# Test case for when no data is returned
@patch('requests.get')
def test_get_temp_no_data(mock_get):
    # Mock a response with no data
    mocked_response = {
        "type": "FeatureCollection",
        "features": []
    }
    
    mock_response = MagicMock()
    mock_response.text = json.dumps(mocked_response)
    mock_get.return_value = mock_response
    
    # Call the function
    temp_map = get_temp("2024-11-23T00:00:00Z", "2024-11-23T02:00:00Z")
    
    # Assertions
    assert len(temp_map) == 0  # No data should return an empty map
