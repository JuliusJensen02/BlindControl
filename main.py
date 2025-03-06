import multiprocessing

from scripts.data_to_csv import query_data_period
from scripts.greybox_fitting import get_constants
from scripts.prediction import predict_for_date

def main():
    query_data_period("2025-03-01T00:00:00Z", "2025-03-05T00:00:00Z")
    constants = get_constants("2024-11-20T00:00:00Z", 50, True)
    print(constants)
    predict_for_date("2025-03-03T00:00:00Z", constants, True)

if __name__ == '__main__':
    # This is required to ensure proper initialization of multiprocessing
    multiprocessing.freeze_support()
    main()


