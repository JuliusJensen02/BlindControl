import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scripts.plot import plot_df
from test_data_processing import sample_data

@patch('plotly.express.line')  # Mocking px.line to prevent it from plotting
def test_plot_df(mock_px_line, sample_data):
    # Mock the returned figure from px.line to avoid actual plotting
    mock_fig = MagicMock(spec=go.Figure)
    mock_px_line.return_value = mock_fig

    # Call the plot function
    plot_df(sample_data)

    # Verify that px.line was called with the correct parameters
    mock_px_line.assert_called_once_with(sample_data, x="time", y=["room_temp", "temp_predictions"], title="Time-Series Data (Plotly)")

    # Verify that the figure was updated with proper axis titles
    mock_fig.update_xaxes.assert_called_once_with(title="Time", tickangle=45)
    mock_fig.update_yaxes.assert_called_once_with(title="Temperature")
    mock_fig.show.assert_called_once()  # Ensure that fig.show() is called to display the plot