import torch


class TemperatureODE(torch.nn.Module):
    """
    Function that gets the values used to solve the ODE.
    Args:
        T_a: The ambient temperature.
        S_t: The solar effect.
        h_s: The heater effect.
        O: The occupancy effect.
        constants: The constants used to predict the temperature.
        heater_max: The maximum heater output.
    """
    def __init__(self, T_a, S_t, h_s, O, constants, heater_max):
        super().__init__()
        self.T_a = T_a
        self.S_t = S_t
        self.h_s = h_s
        self.c_s = c_s
        self.O = O
        self.a_a, self.a_s, self.a_h, self.a_v, self.a_o = constants
        self.heater_max = heater_max

   """
   Calculates the ventilation effect based on the ambient temperature given a function and the openness of a valve
    Args:
        idx: The index of the current time step.
        T: The previously calculated temperature.
    Returns:
        A temperature difference based on the ambient temperature, current temperature and the openness for a valve.
    """
    def V(self, idx: int, T: float) -> float:
        ventilation_temp = self.T_a[idx]
        ventilation_valve = 0.3
        if self.T_a[idx] <= 5:
            ventilation_temp = 21
        elif 5 < self.T_a[idx] <= 17.8:
            ventilation_temp = -0.25 * self.T_a[idx] + 22.25

        if T > self.c_s[idx]:
            ventilation_valve = 1

        return ventilation_valve * (ventilation_temp - T)


    """
    Moves forward to the next step of the ODE.
    Args:
        t: The current time.
        y: The initial values of the temperature and heater.
    Returns:
        An array containing the changes of the temperature and heater.
    """
    def forward(self, t: float, y: float) -> torch.Tensor:
        T, H = y[0], y[1]
        idx = min(int(t), len(self.T_a) - 1)

        # Heater function packed into the derivative (better for performance)
        charging = torch.sigmoid((self.h_s[idx] - T) * 20)
        dH = 0.02 * (self.heater_max - H) * charging \
             - 0.02 * H * (1 - charging)

        dT = ((self.T_a[idx] - T) * self.a_a +
              self.S_t[idx] * self.a_s +
              H * self.a_h +
              self.V(idx, T) * self.a_v +
              self.O[idx] * self.a_o)
        return torch.stack([dT, dH])