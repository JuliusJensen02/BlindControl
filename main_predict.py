import argparse
import csv
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from get_simulation_data import convert_uppaal_to_df
from scripts.prediction import predict_for_date
from scripts.constants import rooms, periods


parser = argparse.ArgumentParser()
parser.add_argument("--period", required=True, type=str)
parser.add_argument("--interval", required=True, type=int)
args = parser.parse_args()

chosen_room = rooms["1.213"]
prediction_interval = args.interval

results = {
    "Bang-Bang": {
        "sum_minutes_out_setpoint": 0,
        "sum_mean_dist_opt_temp": 0,
        "total_daily_dist_setpoints": 0,
        "sum_mean_dist_setpoints": 0,
        "df": pd.DataFrame()
    },
    "UPPAAL_q": {
        "sum_minutes_out_setpoint": 0,
        "sum_mean_dist_opt_temp": 0,
        "total_daily_dist_setpoints": 0,
        "sum_mean_dist_setpoints": 0,
        "df": pd.DataFrame()
    },
    "UPPAAL_m": {
        "sum_minutes_out_setpoint": 0,
        "sum_mean_dist_opt_temp": 0,
        "total_daily_dist_setpoints": 0,
        "sum_mean_dist_setpoints": 0,
        "df": pd.DataFrame()
    }
}

start_date = datetime.strptime(periods[args.period]["start"], "%Y-%m-%d")

for day in range(periods[args.period]["days"]):
    current_date = datetime.strftime(start_date + timedelta(days=day), "%Y-%m-%dT%H:%M:%SZ")
    results["Bang-Bang"]["df"] = predict_for_date(chosen_room,
                          current_date,
                          prediction_interval,
                          args.period)

    results["UPPAAL_q"]["df"] = convert_uppaal_to_df(day+1, args.period, prediction_interval, "Q-Learning")
    results["UPPAAL_m"]["df"] = convert_uppaal_to_df(day+1, args.period, prediction_interval, "M-Learning")

    for method in ["Bang-Bang", "Q-Learning", "M-Learning"]:
        sum_mean_dist_setpoints_temp = 0
        sum_mean_dist_opt_temp_temp = 0

        for row in results[method]["df"].itertuples():
            if row.temp_predictions > row.cooling_setpoint or row.temp_predictions < row.heating_setpoint:
                results[method]["sum_minutes_out_setpoint"] += 1
                if row.temp_predictions > row.cooling_setpoint:
                    results[method]["total_daily_dist_setpoints"] += np.abs(row.temp_predictions - row.cooling_setpoint)
                    sum_mean_dist_setpoints_temp += np.abs(row.temp_predictions - row.cooling_setpoint)
                else:
                    results[method]["total_daily_dist_setpoints"] += np.abs(row.temp_predictions - row.heating_setpoint)
                    sum_mean_dist_setpoints_temp += np.abs(row.temp_predictions - row.heating_setpoint)

            results[method]["opt_setpoint"] = (row.cooling_setpoint - row.heating_setpoint) / 2 + row.heating_setpoint
            sum_mean_dist_opt_temp_temp += np.abs(row.temp_predictions - results[method]["opt_setpoint"])

        results[method]["sum_mean_dist_setpoints"] += sum_mean_dist_setpoints_temp / len(results[method]["df"])
        results[method]["sum_mean_dist_opt_temp"] += sum_mean_dist_opt_temp_temp / len(results[method]["df"])

    results[method]["sum_mean_dist_setpoints"] /= periods[args.period]["days"]
    results[method]["sum_mean_dist_opt_temp"] /= periods[args.period]["days"]
    results[method]["total_daily_dist_setpoints"] /= periods[args.period]["days"]


with open("comparison_data.csv", "a", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Bang-Bang", args.period, args.interval,
                     sum_minutes_out_setpoint, sum_mean_dist_opt_temp,
                     total_daily_dist_setpoints, sum_mean_dist_setpoints])
    writer.writerow(["UPPAAL", args.period, args.interval,
                    uppaal_sum_minutes_out_setpoint, uppaal_sum_mean_dist_opt_temp,
                    uppaal_total_daily_dist_setpoints, uppaal_sum_mean_dist_setpoints])
print(f"Period: {args.period}, Interval: {args.interval}")