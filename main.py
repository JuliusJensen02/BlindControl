from scripts.greybox_fitting import get_constants, predict_for_date

constants = get_constants("2024-11-25T00:00:00Z", 1)

predict_for_date("2024-11-25T00:00:00Z", constants, True)