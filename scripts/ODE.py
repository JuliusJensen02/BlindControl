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
       Calculates the heating effect based on the ambient temperature given a function and the openness of a valve
        Args:
            idx: The index of the current time step.
            T: The previously calculated temperature.
        Returns:
            A temperature difference based on the ambient temperature, current temperature and the openness for a valve.
        """

    def H(self, idx: int, T: float) -> float:
        heater_valve = 0
        heater_temp = 40
        if T <= self.h_s[idx]:
            heater_valve = 1
        elif T > self.h_s[idx]:
            heater_valve = 0

        if self.T_a[idx] <= -12:
            heater_temp = 77
        elif -12 < self.T_a[idx] <= 5:
            heater_temp = -self.T_a[idx] + 65
        elif 5 < self.T_a[idx] <= 20:
            heater_temp = -1.33 * self.T_a[idx] + 66.67

        return heater_valve * (heater_temp - T)

    """
    Moves forward to the next step of the ODE.
    Args:
        t: The current time.
        y: The initial values of the temperature and heater.
    Returns:
        An array containing the changes of the temperature and heater.
    """
    def forward(self, t: float, y: float) -> torch.Tensor:
        T = y[0]
        idx = min(int(t), len(self.T_a) - 1)

        dT = ((self.T_a[idx] - T) * self.a_a +
              self.S_t[idx] * self.a_s +
              self.H(idx, T) * self.a_h +
              self.V(idx, T) * self.a_v +
              self.O[idx] * self.a_o)
        return dT