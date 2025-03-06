import multiprocessing

from scripts.data_to_csv import query_data_period
from scripts.greybox_fitting import get_constants
from scripts.prediction import predict_for_date

#query_data_period("2025-02-11T00:00:00Z", "2025-03-01T00:00:00Z")

def main():
    constants = get_constants("2024-11-27T00:00:00Z", 20)
    print(constants)
    predict_for_date("2025-02-06T00:00:00Z", constants, True)

if __name__ == '__main__':
    # This is required to ensure proper initialization of multiprocessing
    multiprocessing.freeze_support()
    main()


