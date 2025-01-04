import adafruit_mmc56x3
from math import atan2, pi


class Compass:
    def __init__(self, i2c):
        self.i2c = i2c
        self.magnetometer = adafruit_mmc56x3.MMC5603(i2c)

    def _all(self):
        x, y, z = self.magnetometer.magnetic
        c = self.magnetometer.temperature
        return x, y, z, c

    def raw_direction(self):
        '''Returns a 3 component vector pointing to magnetic north. '''
        return self.magnetometer.magnetic

    def direction(self):
        '''
        Returns an angle which points to magnetic North
        clockwise from the y axis
        0 deg is North
        90 deg is East
        180 deg is South
        270 deg is West
        '''
        x, y, _ = self.raw_direction()
        return atan2(x, y) * 180 / pi


    def temperature(self):
        return self.magnetometer.temperature
