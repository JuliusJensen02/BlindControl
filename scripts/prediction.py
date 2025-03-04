import numpy as np

from scripts.data_processing import convert_csv_to_df
from scripts.data_to_csv import reset_csv, query_data
from scripts.derivative_functions import predict_temperature
from scripts.plot import plot_df

'''
@param start_time: a string of the date to predict
@param constants: the constants from the training data
@param plot: a boolean value for whether to plot the result of the prediction
@returns: a DataFrame with the predictions
Predicts the room temperature 
'''
def predict_for_date(start_time, constants, plot):
    reset_csv()
    query_data(start_time, 1)
    df = convert_csv_to_df("data/data.csv")

    #Get the values from the dataframe
    room_temp = df["room_temp"].values
    ambient_temp = df["ambient_temp"].values
    solar_watt = df["solar_watt"].values

    #Save the predictions to the dataframe
    df['temp_predictions'] = predict_temperature(constants.values(), room_temp, ambient_temp, solar_watt)

    #Plot the data if plot is true
    if plot:
        plot_df(df)
        return
    return df