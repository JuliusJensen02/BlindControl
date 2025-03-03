import numpy as np

from scripts.data_processing import convert_csv_to_df
from scripts.data_to_csv import reset_csv, query_data
from scripts.derivative_functions import predict_temperature
from scripts.plot import plot_df


def predict_for_date(start_time, constants, plot):
    reset_csv()
    query_data(start_time, 1)
    df = convert_csv_to_df("data/data.csv")
    print(df["room_temp"][0])
    room_temp = df["room_temp"].values
    print(room_temp[0])
    ambient_temp = df["ambient_temp"].values
    watt = df["watt"].values
    opening_signal = np.zeros_like(df["opening_signal"].values)
    opening_signal = np.full(len(opening_signal), 100)

    df['temp_predictions'] = predict_temperature(constants.values(), room_temp, ambient_temp, watt, opening_signal)

    if plot:
        plot_df(df)
        return
    return df