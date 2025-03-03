from scripts.greybox_fitting import get_constants, predict_for_date

constants = get_constants("2024-11-24T00:00:00Z", 30)

predict_for_date("2025-02-11T00:00:00Z", constants, True)