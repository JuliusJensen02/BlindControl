import numpy as np

'''
:param df = DataFrame()
Loops through the parameters alpha_a, alpha_s, and other_factors in order 
to determine the best fit for the given data in the DataFrame
'''
def fitting(df):
    #Initial guesses
    controller = 1
    alpha_a_guess = 0
    alpha_s_guess = 0
    other_factors = -1
    df_len = len(df) #Saves the length of the df for performance
    best_fit = {'a': 0, 's': 0, 'min_sse': float('inf'), "other_factors": 0}
    for i in range(10): #alpha_a loop
        for j in range(10): #alpha_s loop
            for k in range(20): #other_factors loop
                df['temp_predictions'] = temp_prediction(df, alpha_a_guess, alpha_s_guess, controller, df_len, other_factors)
                sse = sum_squared_error(df['room_temp'], df['temp_predictions'])
                if sse < best_fit['min_sse']: # If SSE is smaller than the previous best SSE then override
                    best_fit['min_sse'] = sse
                    best_fit['a'] = alpha_a_guess
                    best_fit['s'] = alpha_s_guess
                    best_fit['other_factors'] = other_factors
                other_factors += 0.1
            alpha_s_guess += 0.01
            other_factors = 0 #reset other_factors
        alpha_a_guess += 0.01
        alpha_s_guess = 0 #reset alpha_s
        other_factors = 0 #reset other_factors
        print(alpha_a_guess)
    print(best_fit)
    #Predict the using the best fit
    df['temp_predictions'] = temp_prediction(df, best_fit["a"], best_fit["s"], controller, df_len, best_fit["other_factors"])
    return df

'''
:param df = DataFrame()
Loops through the the DataFrame using the parameters alpha_a, alpha_s, and other_factors
in order determine future temperatures
'''
def temp_prediction(df, alpha_a_guess, alpha_s_guess, controller, df_len, other_factors):
    #Convert to nympy arrays for performance
    ambient_temps = df['ambient_temp'].values
    solar_watts = df['watt'].values
    #Preallocate space for temp-predictions for performance
    temp_predictions = np.empty(df_len)
    #Initial room temp is added
    temp_predictions[0] = df['room_temp'].iloc[0]

    #Loop for every item in DataFrame starting from 1 and not 0
    for i in range(1, df_len):
        temp_predicted = temp_change(
            ambient_temps[i], temp_predictions[i-1],
            alpha_a_guess, solar_effect(solar_watts[i]),
            alpha_s_guess, controller, other_factors
        )
        temp_predictions[i] = temp_predictions[i-1] + temp_predicted
    print(temp_predictions[-1])
    return temp_predictions.tolist()

'''
SSE
'''
def sum_squared_error(actual, predicted):
    return sum((actual - predicted)**2)


'''
Solar effect based on mean value for window size and G value
'''
def solar_effect(df_watt):
    G = 0.7
    mean_window_area_group = 4.25
    return df_watt * G * mean_window_area_group


'''
The differential equation for prediction
'''
def temp_change(ambient_temp, room_temp, alpha_a_guess, alpha_s_guess, solar_impact, controller, other_factors):
    return (ambient_temp - room_temp) * alpha_a_guess + solar_impact * alpha_s_guess * controller + other_factors
