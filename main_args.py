import argparse
import multiprocessing
from scripts.derivative_constants import get_constants

rooms = {
    "1.213": {
        "name": "1.213",
        "window_size": 3.64,
        "heater_effect": 372,
        "source_lux": "_meter"
    },
    "1.215": {
        "name": "1.215",
        "window_size": 5.46,
        "heater_effect": 422,
        "source_lux": "_meter_1.215"
    },
    "1.217": {
        "name": "1.217",
        "window_size": 3.64,
        "heater_effect": 379,
        "source_lux": "_meter"
    },
    "1.229": {
        "name": "1.229",
        "window_size": 5.18,
        "heater_effect": 758,
        "source_lux": "_meter"
    },
    "1.231": {
        "name": "1.231",
        "window_size": 6.86,
        "heater_effect": 758,
        "source_lux": "_meter"
    },
    "1.233": {
        "name": "1.233",
        "window_size": 7,
        "heater_effect": 758,
        "source_lux": "_meter"
    }
}

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
    force_retrain = True
    prediction_interval = args.interval

    print("Getting constants...", flush=True)
    get_constants(chosen_room, training_start_date, training_days, force_retrain, prediction_interval)

if __name__ == '__main__':
    # This is required to ensure proper initialization of multiprocessing
    multiprocessing.freeze_support()
    main()


