import argparse
import multiprocessing
from scripts.constants import rooms
from scripts.solver import train_for_time_frame


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--room", required=True, type=str)
    parser.add_argument("--training-start-date", required=True, type=str)
    parser.add_argument("--training-days", required=True, type=int)
    parser.add_argument("--interval", required=True, type=int)
    parser.add_argument("--prediction-date", type=str)
    args = parser.parse_args()

    chosen_room = rooms[args.room]

    training_start_date = args.training_start_date
    training_days = args.training_days
    prediction_interval = args.interval

    constants, error = train_for_time_frame(chosen_room, training_start_date, training_days, prediction_interval)
    print(constants, flush=True)
    print(error, flush=True)

if __name__ == '__main__':
    # This is required to ensure proper initialization of multiprocessing
    multiprocessing.freeze_support()
    main()


