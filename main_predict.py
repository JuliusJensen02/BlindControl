import argparse
import csv
import multiprocessing
from datetime import datetime, timedelta

import numpy as np

from scripts.prediction import predict_for_date
from scripts.constants import rooms, periods


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--room", required=True, type=str)
    parser.add_argument("--period", required=True, type=str)
    parser.add_argument("--interval", required=True, type=int)
    args = parser.parse_args()

    chosen_room = rooms[args.room]
    prediction_interval = args.interval

    sum_minutes_out_setpoint = 0
    sum_mean_dist_opt_temp = 0
    total_dist_setpoints = 0
    sum_mean_dist_setpoints = 0

    start_date = datetime.strptime(periods[args.period]["start"], "%Y-%m-%d")

    for day in range(periods[args.period]["days"]):
        current_date = datetime.strftime(start_date + timedelta(days=day), "%Y-%m-%dT%H:%M:%SZ")
        df = predict_for_date(chosen_room, current_date, chosen_room["constants"][args.period][prediction_interval], False, prediction_interval)

        sum_mean_dist_setpoints_temp = 0
        sum_mean_dist_opt_temp_temp = 0
        for row in df.itertuples():
            if row.temp_predictions > row.cooling_setpoint or row.temp_predictions < row.heating_setpoint:
                sum_minutes_out_setpoint += 1
                if row.temp_predictions > row.cooling_setpoint:
                    total_dist_setpoints += np.abs(row.temp_predictions - row.cooling_setpoint)
                    sum_mean_dist_setpoints_temp += np.abs(row.temp_predictions - row.cooling_setpoint)
                else:
                    total_dist_setpoints += np.abs(row.temp_predictions - row.heating_setpoint)
                    sum_mean_dist_setpoints_temp += np.abs(row.temp_predictions - row.heating_setpoint)

            opt_setpoint = (row.cooling_setpoint - row.heating_setpoint) / 2 + row.heating_setpoint
            sum_mean_dist_opt_temp_temp += np.abs(row.temp_predictions - opt_setpoint)

        sum_mean_dist_setpoints += sum_mean_dist_setpoints_temp / len(df)
        sum_mean_dist_opt_temp += sum_mean_dist_opt_temp_temp / len(df)
    sum_mean_dist_setpoints /= periods[args.period]["days"]
    sum_mean_dist_opt_temp /= periods[args.period]["days"]
    total_dist_setpoints /= periods[args.period]["days"]

    with open("comparison_data.csv", "a", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["BB", args.period, args.interval,
                         sum_minutes_out_setpoint, sum_mean_dist_opt_temp,
                         total_dist_setpoints, sum_mean_dist_setpoints])
    print(f"Period: {args.period}, Interval: {args.interval}")




if __name__ == '__main__':
    # Initialization of multiprocessing
    #multiprocessing.freeze_support()
    main()


