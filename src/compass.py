import adafruit_mmc56x3


class Compass:
    def __init__(self, i2c):
        self.i2c = i2c
        self.magnetometer = adafruit_mmc56x3.MMC5603(i2c)

    def _all(self):
        x, y, z = self.magnetometer.magnetic
        c = self.magnetometer.temperature
        return x, y, z, c

    def direction(self):
        return self.magnetometer.magnetic

    def temperature(self):
        return self.magnetometer.temperature
