import pytest
import pandas as pd
from io import StringIO


from scripts.data_processing import normalize, remove_outliers, convert_csv_to_df, smooth


@pytest.fixture
def sample_data():
    csv_data = """time,solar_watt,room_temp,ambient_temp,heating_setpoint,cooling_setpoint,temp_predictions,heating_effects,solar_effects
    2024-12-27 09:03:00+00:00,7.5467529297,22.2,6.6,23.0,25.0,0,0,0
    2024-12-27 09:18:00+00:00,7.5467529297,22.3,6.6,23.0,25.0,0,0,0
    2024-12-27 09:33:00+00:00,7.5467529297,22.3,6.6,23.0,25.0,0,0,0
    2024-12-27 09:48:00+00:00,11.7648925781,22.2,6.6,23.0,25.0,0,0,0
    2024-12-27 10:03:00+00:00,11.7648925781,22.3,6.6,23.0,25.0,0,0,0
    2024-12-27 10:18:00+00:00,13.7916259766,22.4,6.6,23.0,25.0,0,0,0
    2024-12-27 10:34:00+00:00,15.8675537109,22.2,6.6,23.0,25.0,0,0,0
    2024-12-27 10:49:00+00:00,24.3049316406,22.4,6.6,23.0,25.0,0,0,0
    2024-12-27 11:06:00+00:00,22.1949462891,22.4,6.6,23.0,25.0,0,0,0
    2024-12-27 11:21:00+00:00,20.0246582031,22.5,6.6,23.0,25.0,0,0,0
    2024-12-27 11:36:00+00:00,18.0151367188,22.4,6.4,23.0,25.0,0,0,0
    2024-12-27 11:51:00+00:00,13.8404541016,22.5,6.4,23.0,25.0,0,0,0
    2024-12-27 12:06:00+00:00,18.1911621094,22.5,6.4,23.0,25.0,0,0,0
    2024-12-27 12:21:00+00:00,16.1551513672,22.5,6.4,23.0,25.0,0,0,0
    2024-12-27 12:36:00+00:00,20.3659667969,22.4,6.4,23.0,25.0,0,0,0
    2024-12-27 12:51:00+00:00,18.3323974609,22.4,6.4,23.0,25.0,0,0,0
    2024-12-27 13:06:00+00:00,14.1296386719,22.3,6.4,23.0,25.0,0,0,0
    2024-12-27 13:21:00+00:00,10.0076904297,22.4,30,23.0,25.0,0,0,0
    2024-12-27 13:36:00+00:00,10.0076904297,100,6.2,23.0,25.0,0,0,0
    2024-12-27 13:51:00+00:00,150,22.4,6.2,23.0,25.0,0,0,0
    2024-12-27 14:06:00+00:00,5.9259033203,22.4,6.2,23.0,25.0,0,0,0
    2024-12-27 14:21:00+00:00,3.9113769531,22.4,6.2,23.0,25.0,0,0,0
    2024-12-27 14:36:00+00:00,3.9113769531,22.5,6.1,23.0,25.0,0,0,0
    2024-12-27 14:51:00+00:00,3.9113769531,22.4,6.1,23.0,25.0,0,0,0
    2024-12-27 15:06:00+00:00,3.9113769531,22.6,6.1,23.0,25.0,0,0,0
    2024-12-27 15:21:00+00:00,3.9113769531,22.6,6.1,23.0,25.0,0,0,0
    2024-12-27 15:36:00+00:00,3.9113769531,22.8,6.1,23.0,25.0,0,0,0
    2024-12-27 15:51:00+00:00,3.9113769531,22.9,6.1,23.0,25.0,0,0,0
    2024-12-27 16:06:00+00:00,3.9113769531,22.7,6.1,22.0,26.0,0,0,0
    2024-12-27 16:21:00+00:00,3.9113769531,22.8,6.1,22.0,26.0,0,0,0
    2024-12-27 16:37:00+00:00,3.9113769531,22.6,6.0,22.0,26.0,0,0,0
    2024-12-27 16:52:00+00:00,3.9113769531,22.7,6.0,22.0,26.0,0,0,0
    2024-12-27 17:07:00+00:00,3.9113769531,22.3,6.0,22.0,26.0,0,0,0
    2024-12-27 17:22:00+00:00,3.9113769531,22.3,6.0,22.0,26.0,0,0,0
    2024-12-27 17:37:00+00:00,3.9113769531,22.2,5.9,22.0,26.0,0,0,0
    2024-12-27 17:52:00+00:00,3.9113769531,22.2,5.9,22.0,26.0,0,0,0
    2024-12-27 18:07:00+00:00,3.9113769531,22.2,5.9,22.0,26.0,0,0,0
    2024-12-27 18:22:00+00:00,3.9113769531,22.0,5.9,22.0,26.0,0,0,0
    2024-12-27 18:37:00+00:00,3.9113769531,22.0,5.9,22.0,26.0,0,0,0
    2024-12-27 18:52:00+00:00,3.9113769531,22.0,5.9,22.0,26.0,0,0,0
    2024-12-27 19:07:00+00:00,3.9113769531,22.0,5.9,22.0,26.0,0,0,0
    2024-12-27 19:22:00+00:00,3.9113769531,22.0,5.9,22.0,26.0,0,0,0
    2024-12-27 19:37:00+00:00,3.9113769531,22.0,5.9,22.0,26.0,0,0,0
    2024-12-27 19:52:00+00:00,3.9113769531,21.9,5.9,22.0,26.0,0,0,0
    2024-12-27 20:07:00+00:00,3.9113769531,22.0,5.9,22.0,26.0,0,0,0
    2024-12-27 20:22:00+00:00,3.9113769531,22.4,5.9,22.0,26.0,0,0,0
    2024-12-27 20:38:00+00:00,3.9113769531,22.2,5.9,22.0,26.0,0,0,0
    2024-12-27 20:53:00+00:00,3.9113769531,22.0,5.9,22.0,26.0,0,0,0
    2024-12-27 21:10:00+00:00,3.9113769531,22.1,5.9,22.0,26.0,0,0,0
    2024-12-27 21:25:00+00:00,3.9113769531,22.0,5.9,22.0,26.0,0,0,0
    2024-12-27 21:40:00+00:00,3.9113769531,22.0,5.9,22.0,26.0,0,0,0
    """
    df = pd.read_csv(StringIO(csv_data))
    return df

# Test normalize function
def test_normalize(sample_data):
    df = sample_data.copy()
    normalized_df = normalize(df.copy())
    assert 'solar_watt' in df

    # Normalize the 'solar_watt' column
    solar_min = df['solar_watt'].min()
    solar_max = df['solar_watt'].max()
    expected_solar_watt = 20 + (df['solar_watt'] - solar_min) / (solar_max - solar_min)

    # Compare the normalized values
    try:
        pd.testing.assert_series_equal(normalized_df['solar_watt'], expected_solar_watt)
    except AssertionError:
        raise AssertionError(f"Normalization failed")


# Test remove_outliers function
def test_remove_outliers(sample_data):
    df = sample_data.copy()
    df_cleaned = remove_outliers(df)
    assert len(df_cleaned) < len(df), "Outlier removal did not work as expected"
    assert df_cleaned['solar_watt'].max() <= df['solar_watt'].max(), f"Outliers detected in solar_watt after outlier removal."
    assert df_cleaned['solar_watt'].min() >= df['solar_watt'].min(), f"Outliers detected in solar_watt after outlier removal."
    
    assert df_cleaned['room_temp'].max() <= df['room_temp'].max(), f"Outliers detected in room_temp after outlier removal."
    assert df_cleaned['room_temp'].min() >= df['room_temp'].min(), f"Outliers detected in room_temp after outlier removal."

    assert df_cleaned['ambient_temp'].max() <= df['ambient_temp'].max(), f"Outliers detected in ambient_temp after outlier removal."
    assert df_cleaned['ambient_temp'].min() >= df['ambient_temp'].min(), f"Outliers detected in ambient_temp after outlier removal."

# Test smooth function
def test_smooth(sample_data):
    df_smoothed = smooth(sample_data.copy())
    assert 'room_temp' in df_smoothed
    assert not df_smoothed['room_temp'].equals(sample_data['room_temp']), "Smoothing did not change values"
