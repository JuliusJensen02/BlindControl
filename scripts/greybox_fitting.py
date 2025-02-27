import numpy as np

def fitting(df):
    controller = 1
    alpha_a_guess = 0
    alpha_s_guess = 0
    other_factors = -1
    df_len = len(df) - 1
    best_fit = {'a': 0, 's': 0, 'min_sse': float('inf'), "other_factors": 0}
    for i in range(10):
        for j in range(10):
            for k in range(20):
                df['temp_predictions'] = temp_prediction(df, alpha_a_guess, alpha_s_guess, controller, df_len, other_factors)
                sse = sum_squared_error(df['room_temp'], df['temp_predictions'])
                if sse < best_fit['min_sse']:
                    best_fit['min_sse'] = sse
                    best_fit['a'] = alpha_a_guess
                    best_fit['s'] = alpha_s_guess
                    best_fit['other_factors'] = other_factors
                other_factors += 0.1
            alpha_s_guess += 0.01
            other_factors = 0
        alpha_a_guess += 0.01
        alpha_s_guess = 0
        other_factors = 0
        print(alpha_a_guess)
    print(best_fit)
    df['temp_predictions'] = temp_prediction(df, best_fit["a"], best_fit["s"], controller, df_len, best_fit["other_factors"])
    df = df[:-1]
    return df


def temp_prediction(df, alpha_a_guess, alpha_s_guess, controller, df_len, other_factors):
    ambient_temps = df['ambient_temp'].values
    solar_watts = df['watt'].values
    temp_predictions = np.empty(df_len + 1)

    temp_predictions[0] = df['room_temp'].iloc[0]

    for i in range(1, df_len):
        temp_predicted = temp_change(
            ambient_temps[i], temp_predictions[i-1],
            alpha_a_guess, solar_effect(solar_watts[i]),
            alpha_s_guess, controller, other_factors
        )
        temp_predictions[i] = temp_predictions[i-1] + temp_predicted

    return temp_predictions.tolist()

def sum_squared_error(actual, predicted):
    return sum((actual - predicted)**2)

def solar_effect(df_watt):
    G = 0.7
    mean_window_area_group = 4.25
    return df_watt * G * mean_window_area_group

def temp_change(ambient_temp, room_temp, alpha_a_guess, alpha_s_guess, solar_impact, controller, other_factors):
    return (ambient_temp - room_temp) * alpha_a_guess + solar_impact * alpha_s_guess * controller + other_factors
