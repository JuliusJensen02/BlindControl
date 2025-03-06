from datetime import datetime
from scripts.data_to_csv import cache_constants, hour_rounder

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