rooms = {
    "1.213": {
        "name": "1.213",
        "window_size": 3.64,
        "heater_effect": 372,
        "source_lux": "_meter",
        "max_people": 7,
        "prob_dist":    [[0.5, 0.25, 0.15, 0.05, 0.03, 0.01, 0.01],
                        [0.1, 0.15, 0.2, 0.2, 0.15, 0.1, 0.1],
                        [0.05, 0.1, 0.15, 0.2, 0.2, 0.15, 0.15],
                        [0.2, 0.25, 0.2, 0.15, 0.1, 0.06, 0.04]],
        "values": [1,2,3,4,5,6,7],
        "group": True,
        "constants": {
            "winter": {
                1: [1.96029540e-04, 3.73810088e-06, 5.80891322e-04, 2.78284372e-03, 9.10857409e-06],
                4: [1.62629173e-04, 1.12732988e-05, 5.22446549e-04, 1.71810045e-03, 9.51243886e-06],
                12: [9.56843021e-05, 1.51456800e-05, 3.31177618e-04, 8.52353097e-04, 1.06713737e-05],
                24: [8.34092009e-05, 1.86889102e-05, 3.15249155e-04, 5.59468955e-04, 1.14423698e-05]
            },
            "spring": {
                1: [2.30437721e-05, 1.01921563e-05, 3.84168817e-04, 1.86791327e-03, 7.40400684e-06],
                4: [1.57778696e-05, 7.61306402e-06, 3.68268960e-04, 1.02288733e-03, 9.66533311e-06],
                12: [3.99459828e-05, 6.82779926e-06, 1.83458564e-04, 7.12112426e-04, 1.21252858e-05],
                24: [5.67315175e-05, 5.80486886e-06, 9.60538557e-05, 3.42099083e-04, 1.00894284e-05]
            },
            "december": {
                1: [1.78136022e-04, 2.56259938e-05, 6.38230324e-04, 3.15032649e-03, 8.30384750e-06],
                4: [1.76084057e-04, 1.30598723e-05, 6.01668973e-04, 1.81147788e-03, 6.54253673e-06],
                12: [1.08143047e-04, 1.98327617e-05, 2.63051167e-04, 6.01914294e-04, 5.57395366e-06],
                24: [9.72531152e-05, 4.91833485e-06, 3.38081634e-04, 4.73849362e-04, 6.29814099e-06]
            },
            "january": {
                1: [2.54705440e-04, 2.85921223e-05, 5.30575518e-04, 2.43618666e-03, 9.82986150e-06],
                4: [2.14601319e-04, 4.09707965e-06, 4.66841015e-04, 1.68217740e-03, 1.20699767e-05],
                12: [1.23994750e-04, 7.38363268e-06, 3.12006099e-04, 9.02976181e-04, 1.47684421e-05],
                24: [9.30007256e-05, 8.44278406e-06, 2.98587155e-04, 5.78763794e-04, 1.54663247e-05]
            },
            "february": {
                1: [1.50844920e-04, 8.75617766e-06, 5.73097049e-04, 2.75981319e-03, 9.20123963e-06],
                4: [9.02544926e-05, 1.72383620e-05, 4.96279020e-04, 1.65449966e-03, 9.97523263e-06],
                12: [5.12461264e-05, 7.88367014e-05, 4.28591219e-04, 1.07599710e-03, 1.17789673e-05],
                24: [5.74609556e-05, 5.61835875e-05, 3.08437863e-04, 6.32119312e-04, 1.26908135e-05]
            },
            "march": {
                1: [2.85013718e-05, 1.28574339e-05, 6.42823016e-04, 2.52334702e-03, 2.63565891e-06],
                4: [5.92786850e-05, 9.31173540e-06, 4.88003218e-04, 1.31507921e-03, 5.31182888e-06],
                12: [5.23115491e-05, 1.51746103e-06, 3.10738477e-04, 1.00844330e-03, 1.11496002e-05],
                24: [5.94131352e-05, 5.84967916e-06, 1.55904540e-04, 5.93600625e-04, 9.22861538e-06]
            },
            "april": {
                1: [7.63070876e-05, 7.43803621e-06, 1.16892811e-04, 1.19063172e-03, 1.23312997e-05],
                4: [2.91729729e-05, 5.85777027e-06, 2.44543560e-04, 7.20955726e-04, 1.41639542e-05],
                12: [2.71682310e-05, 1.23151488e-05, 5.19359872e-05, 4.05903855e-04, 1.31334942e-05],
                24: [5.39605126e-05, 5.75856488e-06, 3.42081485e-05, 8.22141560e-05, 1.09789352e-05]
            }
        }
    }
}

periods = {
    "winter": {
        "start": "2025-02-17",
        "days": 7,
        "simulation_day": "2025-02-17",
    },
    "spring": {
        "start": "2025-04-14",
        "days": 7,
        "simulation_day": "2025-04-14",
    },
    "december": {
        "start": "2024-12-16",
        "days": 7,
        "simulation_day": "2024-12-16",
    },
    "january": {
        "start": "2025-01-13",
        "days": 7,
        "simulation_day": "2025-01-13",
    },
    "february": {
        "start": "2025-02-17",
        "days": 7,
        "simulation_day": "2025-02-17",
    },
    "march": {
        "start": "2025-03-17",
        "days": 7,
        "simulation_day": "2025-03-17",
    },
    "april": {
        "start": "2025-04-14",
        "days": 7,
        "simulation_day": "2025-04-14",
    },
}

prediction_intervals = [1, 4, 12, 24]