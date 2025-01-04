import board
import logging
from drive import AzDrive
from compass import Compass


logging.basicConfig(level=logging.DEBUG)

# azimuth drive
i2c = board.I2C()
compass = Compass(i2c)
drive = AzDrive(compass, 29/149, 10, board.D19, board.D26, board.D13, board.D6, board.D5)
#drive.home()
