import multiprocessing

from experiments.uppaal_jobs.plot_simulation_data import convert_uppaal_to_df
from scripts.data_processing import preprocess_data_for_all_dates
from scripts.query import query_data_period
from scripts.constants import get_constants
from scripts.prediction import predict_for_date

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
    chosen_room = rooms["1.213"]

    query_start_date = "2025-03-25T00:00:00Z"
    query_end_date = "2025-04-01T00:00:00Z"
    run_query = False
    preprocess_data = False

    train = True
    training_start_date = "2024-12-01T00:00:00Z"
    training_days = 31
    force_retrain = True
    prediction_interval = 60

    predict_date = "2025-02-21T00:00:00Z"

    #if run_query:
    #    query_data_period(query_start_date, query_end_date, chosen_room)
    #if preprocess_data:
    #    preprocess_data_for_all_dates(query_start_date, query_end_date, chosen_room)
    #if train:
        #constants = get_constants(chosen_room, training_start_date, training_days, force_retrain, prediction_interval)
    predict_for_date(chosen_room, predict_date, [1.99706603e-04, 1.12559767e-05, 7.83316484e-05, 2.98706584e-04,
       2.33775480e-05], True, 1341)

if __name__ == '__main__':
    # Initialization of multiprocessing
    multiprocessing.freeze_support()
    main()


