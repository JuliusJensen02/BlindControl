import argparse
import multiprocessing

from scripts.prediction import predict_for_date
from scripts.constants import rooms

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--room", required=True, type=str)
    parser.add_argument("--predict-date", required=True, type=str)
    parser.add_argument("--prediction-interval", required=True, type=int)
    args = parser.parse_args()

    chosen_room = rooms[args.room]

    predict_date = args.training_days+"T00:00:00Z"
    prediction_interval = args.interval

    predict_date = "2025-02-17"

    predict_for_date(chosen_room, predict_date, chosen_room["constants"], True, prediction_interval)

if __name__ == '__main__':
    # Initialization of multiprocessing
    multiprocessing.freeze_support()
    main()


