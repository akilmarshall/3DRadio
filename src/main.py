import board
import logging
from drive import AzDrive
from compass import Compass
from gps import GPS


logging.basicConfig(level=logging.DEBUG)

i2c = board.I2C()
compass = Compass(i2c)
gps = GPS(i2c)
# azimuth drive
drive = AzDrive(compass, 29/149, 10, board.D19, board.D26, board.D13, board.D6, board.D5)
#drive.home()
