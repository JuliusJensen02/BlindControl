#Rooms 1.229, 1.231, 1.233 are offices, Rooms 1.213, 1.215, 1.217 are group rooms
rooms = ["1.213", "1.215", "1.217", "1.229", "1.231", "1.233"]

#Solar in watt/m^2
sources_tmv23 = ["/TM023_1_20_1103/SG01/Solar_panel_south"]

#opening_signal is for heater, occupancy (pir(source: /TM023_3_20_1.204/Lon/Net/Rum_1.233/PIR_activity_1.233) & lux(source: /TM023_3_20_1.204/Lon/Net/Rum_1.233/Lux_meter))
sensor_types_rooms = ["window_open", "temperature", "opening_signal", "occupancy", "co2"]
sensor_types_rooms_units = ["bool", "C", "%", "bool/lux", "ppm"]

mean_window_size_office = 6.35
mean_window_size_group = 4.25