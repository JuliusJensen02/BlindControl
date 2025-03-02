import numpy as np
import pandas as pd
from scipy.optimize import minimize

from scripts.data_processing import remove_outliers, smooth, normalize
from scripts.greybox_fitting import temp_prediction, solar_effect, temp_change
from scripts.plot import plot_df

# Load CSV file
df = pd.read_csv("../data/data.csv", parse_dates=["time"])  # Replace with actual filename

df = remove_outliers(df)
df = smooth(df)
#df = normalize(df)

# Ensure data is sorted by time
df = df.sort_values(by="time")

# Extract relevant columns
t_r = df["room_temp"].values
t_a = df["ambient_temp"].values
S = df["watt"].values

def predict_temperature(params):
    alpha_a, alpha_s, beta = params
    t_r_pred = np.empty(len(t_r))
    t_r_pred[0] = t_r[0]  # Set initial condition

    for t in range(1, len(t_r)):
        temp_predicted = temp_change(
            t_a[t-1], t_r_pred[t-1],
            alpha_a, alpha_s, solar_effect(S[t-1]),
            1, beta
        )
        t_r_pred[t] = t_r_pred[t-1] + temp_predicted
    return t_r_pred


def mean_absolute_error(params):
    t_r_pred = predict_temperature(params)
    return np.mean(np.abs(t_r - t_r_pred))

def mean_squared_error(params):
    t_r_pred = predict_temperature(params)
    return np.mean((t_r - t_r_pred)**2)

# Initial guess for parameters
initial_guess = np.array([0.01, 0.001, 0.1])  # alpha_a, alpha_S, beta

# Optimize parameters to minimize SSE
result = minimize(mean_absolute_error, initial_guess, method="L-BFGS-B")

# Extract optimized constants
alpha_a_opt, alpha_S_opt, beta_opt = result.x
print(f"Optimized parameters: αa = {alpha_a_opt}, αS = {alpha_S_opt}, β = {beta_opt}")
print(f"Final SSE: {result.fun}")

df['temp_predictions'] = temp_prediction(df, alpha_a_opt, alpha_S_opt, 1, len(df), beta_opt)
plot_df(df)
