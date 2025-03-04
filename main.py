from scripts.greybox_fitting import get_constants
from scripts.prediction import predict_for_date

constants = get_constants("2024-11-25T00:00:00Z", 1, True)
print(constants)
predict_for_date("2024-12-27T00:00:00Z", constants, True)