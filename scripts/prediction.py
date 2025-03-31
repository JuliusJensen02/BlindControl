from datetime import datetime
import numpy as np
from data_processing import get_raw_data_as_df
from scripts.derivative_functions import predict_temperature_for_prediction
from scripts.plot import plot_df

'''
@param start_time: a string of the date to predict
@param constants: the constants from the training data
@param plot: a boolean value for whether to plot the result of the prediction
@returns: a DataFrame with the predictions
Predicts the room temperature 
'''
def predict_for_date(room, start_time, constants, plot):
    df = get_raw_data_as_df(datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ"),room)

    #Get the values from the dataframe
    room_temp = df["room_temp"].to_numpy()
    ambient_temp = df["ambient_temp"].to_numpy()
    solar_watt = df["solar_watt"].to_numpy()
    heating_setpoint = df["heating_setpoint"].to_numpy()
    cooling_setpoint = df["cooling_setpoint"].to_numpy()
    heating_effects = np.zeros_like(heating_setpoint)
    solar_effects = np.zeros_like(solar_watt)
    lux = df["lux"].to_numpy()
    wind = df["wind"].to_numpy()

    #Save the predictions to the dataframe
    df['temp_predictions'] = predict_temperature_for_prediction(room, constants.values(), room_temp, ambient_temp, solar_watt,
                                heating_setpoint, cooling_setpoint, lux, wind, heating_effects, solar_effects)
    df['heating_effects'] = heating_effects
    df['solar_effects'] = solar_effects
    #df = smooth(df, 'temp_predictions')
    #Plot the data if plot is true
    if plot:
        plot_df(df)
        return
    return df