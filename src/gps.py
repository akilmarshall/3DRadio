import adafruit_gps
import board


class GPS:
    def __init__(self, i2c):
        self.i2c = i2c
        self.gps = adafruit_gps.GPS_GtopI2C(i2c)  # Use I2C interface
        # Turn on the basic GGA and RMC info
        self.gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
        # Set update rate to once a second
        self.gps.send_command(b"PMTK220,1000")


    def raw_read(self):
        data = self.gps.read(32)
        return "".join([chr(b) for b in data])
