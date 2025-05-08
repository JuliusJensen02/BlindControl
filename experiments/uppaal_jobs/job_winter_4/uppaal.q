strategy OptimizeTemperature = minE (cost) [<=(control_interval * 2) * __PERIOD__] : <> counter == init_time + (control_interval * 2)
simulate [<=30;1]{blocked, blinds, T_r} under OptimizeTemperature