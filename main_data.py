import multiprocessing

from scripts.data_processing import preprocess_data_for_all_dates
from scripts.query import query_data_period
from scripts.constants import rooms

def main():
    chosen_room = rooms["1.213"]

    query_start_date = "2024-11-20T00:00:00Z"
    query_end_date = "2025-04-01T00:00:00Z"

    query_data_period(query_start_date, query_end_date, chosen_room)
    preprocess_data_for_all_dates(query_start_date, query_end_date, chosen_room)


if __name__ == '__main__':
    # Initialization of multiprocessing
    multiprocessing.freeze_support()
    main()