import multiprocessing

from scripts.query_data import query_data_period
from scripts.derivative_constants import get_constants
from scripts.prediction import predict_for_date
#TODO: Add relevant info to rooms for easy query
rooms = {
    "1.213": {
        "name": "1.213",
        "window_size": 3.64,
        "heater_effect": 372
    },
    "1.215": {
        "name": "1.215",
        "window_size": 5.46,
        "heater_effect": 422
    },
    "1.217": {
        "name": "1.217",
        "window_size": 3.64,
        "heater_effect": 379
    },
    "1.229": {
        "name": "1.229",
        "window_size": 5.18,
        "heater_effect": 758
    },
    "1.231": {
        "name": "1.231",
        "window_size": 6.86,
        "heater_effect": 758
    },
    "1.233": {
        "name": "1.233",
        "window_size": 7,
        "heater_effect": 758
    }
}

def main():
    chosen_room = rooms["1.213"]
    #query_data_period("2024-11-20T00:00:00Z", "2025-03-05T00:00:00Z", chosen_room["name"])
    constants = get_constants(chosen_room, "2024-11-20T00:00:00Z", 50, True)
    print(constants)
    predict_for_date(chosen_room, "2025-03-04T00:00:00Z", constants, True)

if __name__ == '__main__':
    # This is required to ensure proper initialization of multiprocessing
    multiprocessing.freeze_support()
    main()


