from datetime import datetime

import numpy as np

from scripts.data_processing import convert_csv_to_df
from scripts.derivative_functions import predict_temperature
from scripts.plot import plot_df

'''
@param start_time: a string of the date to predict
@param constants: the constants from the training data
@param plot: a boolean value for whether to plot the result of the prediction
@returns: a DataFrame with the predictions
Predicts the room temperature 
'''
def predict_for_date(room, start_time, constants, plot):
    df = convert_csv_to_df(datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ"))

    #Get the values from the dataframe
    room_temp = df["room_temp"].to_numpy()
    ambient_temp = df["ambient_temp"].to_numpy()
    solar_watt = df["solar_watt"].to_numpy()
    heating_setpoint = df["heating_setpoint"].to_numpy()
    cooling_setpoint = df["cooling_setpoint"].to_numpy()
    heating_effects = np.zeros_like(heating_setpoint)
    solar_effects = np.zeros_like(solar_watt)
    lux = df["lux"].to_numpy()


    #Save the predictions to the dataframe
    df['temp_predictions'] = predict_temperature(room, constants.values(), room_temp, ambient_temp, solar_watt,
                                heating_setpoint, cooling_setpoint, lux, heating_effects, solar_effects)
    df['heating_effects'] = heating_effects
    df['solar_effects'] = solar_effects
    #Plot the data if plot is true
    if plot:
        plot_df(df)
        return
    return df