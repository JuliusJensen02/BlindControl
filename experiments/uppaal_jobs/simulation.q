strategy OptimizeTemperature = loadStrategy {} -> {} ("/nfs/home/student.aau.dk/tb30jn/BlindControl/experiments/uppaal_jobs/strategy.json")
simulate [<=30;1]{room_temp} under OptimizeTemperature