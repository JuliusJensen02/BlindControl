strategy OptimizeTemperature = minE (cost) [<=(control_interval * 2) * 12] : <> counter == init_time + (control_interval * 2) * 12
simulate [<=30;1]{blocked, blinds, T_r} under OptimizeTemperature