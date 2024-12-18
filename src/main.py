import board


logging.basicConfig(level=logging.DEBUG)

# azimuth drive
drive = Drive(29/149, 10, board.D19, board.D26, board.D20, board.D21, board.D18)
drive.home()
