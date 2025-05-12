strategy OptimizeTemperature = minE (cost) [<=(control_interval * 2) * 4] : <> counter == init_time + (control_interval * 2) * 4
simulate [<=30;1]{blocked, blinds, T_r} under OptimizeTemperature