strategy OptimizeTemperature = minE (cost) [<=(control_interval * 2) * 1] : <> counter == init_time + (control_interval * 2) * 1
simulate [<=30;1]{blocked, blinds, cost, T_r} under OptimizeTemperature