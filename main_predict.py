import argparse
import csv
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import math

from scripts.get_simulation_data import convert_uppaal_to_df
from scripts.prediction import predict_for_date
from scripts.constants import rooms, periods


parser = argparse.ArgumentParser()
parser.add_argument("--period", required=True, type=str)
parser.add_argument("--interval", required=True, type=int)
parser.add_argument("--room", required=True, type=str)
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

    for method in ["Bang-Bang", "UPPAAL_q", "UPPAAL_m"]:
        sum_mean_dist_setpoints_temp = 0
        sum_mean_dist_opt_temp_temp = 0
        times_outside_setpoint = 0
        last_row_time = 0
        for row in results[method]["df"].itertuples():
            if row.temp_predictions > row.cooling_setpoint or row.temp_predictions < row.heating_setpoint:
                if method == "Bang-Bang":
                    results[method]["sum_minutes_out_setpoint"] += 1
                else:
                    results[method]["sum_minutes_out_setpoint"] += float(row.time) - last_row_time


                if row.temp_predictions > row.cooling_setpoint:
                    results[method]["total_daily_dist_setpoints"] += np.abs(row.temp_predictions - row.cooling_setpoint)
                    sum_mean_dist_setpoints_temp += np.abs(row.temp_predictions - row.cooling_setpoint)
                else:
                    results[method]["total_daily_dist_setpoints"] += np.abs(row.temp_predictions - row.heating_setpoint)
                    sum_mean_dist_setpoints_temp += np.abs(row.temp_predictions - row.heating_setpoint)

                times_outside_setpoint += 1
            if method != "Bang-Bang":
                last_row_time = float(row.time)
            opt_setpoint = (row.cooling_setpoint - row.heating_setpoint) / 2 + row.heating_setpoint
            sum_mean_dist_opt_temp_temp += np.abs(row.temp_predictions - opt_setpoint)

        results[method]["sum_mean_dist_setpoints"] += (sum_mean_dist_setpoints_temp / times_outside_setpoint) if times_outside_setpoint > 0 else 0
        results[method]["sum_mean_dist_opt_temp"] += (sum_mean_dist_opt_temp_temp / len(results[method]["df"]))

for method in ["Bang-Bang", "UPPAAL_q", "UPPAAL_m"]:
    results[method]["sum_mean_dist_setpoints"] /= periods[args.period]["days"]
    results[method]["sum_mean_dist_opt_temp"] /= periods[args.period]["days"]
    results[method]["total_daily_dist_setpoints"] /= periods[args.period]["days"]


with open("comparison_data.csv", "a", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Bang-Bang", args.period, args.interval,
                     results["Bang-Bang"]["sum_minutes_out_setpoint"],
                     results["Bang-Bang"]["sum_mean_dist_opt_temp"],
                     results["Bang-Bang"]["total_daily_dist_setpoints"],
                     results["Bang-Bang"]["sum_mean_dist_setpoints"]
                     ])
    writer.writerow(["UPPAAL Q-Learning", args.period, args.interval,
                    results["UPPAAL_q"]["sum_minutes_out_setpoint"],
                    results["UPPAAL_q"]["sum_mean_dist_opt_temp"],
                    results["UPPAAL_q"]["total_daily_dist_setpoints"],
                    results["UPPAAL_q"]["sum_mean_dist_setpoints"]
                     ])
    writer.writerow(["UPPAAL M-Learning", args.period, args.interval,
                     results["UPPAAL_m"]["sum_minutes_out_setpoint"],
                     results["UPPAAL_m"]["sum_mean_dist_opt_temp"],
                     results["UPPAAL_m"]["total_daily_dist_setpoints"],
                     results["UPPAAL_m"]["sum_mean_dist_setpoints"]
                     ])
print(f"Period: {args.period}, Interval: {args.interval}")