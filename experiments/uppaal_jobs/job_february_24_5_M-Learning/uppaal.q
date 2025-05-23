strategy OptimizeTemperature = minE (cost) [<=control_interval * 2 * prediction_interval + 1] : <> clock_time.Done
simulate [<=30;1]{blocked, blinds, cost, T_r, H, C} under OptimizeTemperature