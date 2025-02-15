from time import sleep
from digitalio import DigitalInOut, Direction
from pwmio import PWMOut
from adafruit_motor.stepper import StepperMotor, FORWARD, BACKWARD, MICROSTEP, SINGLE, DOUBLE
from math import atan2, pi, floor, ceil
import logging


LOGGER = logging.getLogger(__name__)


class Drive:
    STEP_ANGLE = 1.8
    RPM = 60

    def __init__(self, ratio: float, microsteps: int, A1, A2, B1, B2, hall):
        LOGGER.debug(f'initializing drive, {ratio = } {microsteps = }')
        self.ratio = ratio  # drive teeth / driven teeth
        self.microsteps = microsteps
        self.theta = Drive.STEP_ANGLE * ratio / microsteps
        self.delay = 0.01

        LOGGER.debug(f'setting up PWM pins {A1 = } {A2 = } {B1 = } {B2 = }')
        # internal PWM frequency of the driver board is 50kHz
        self.A1 = PWMOut(A1)
        self.A2 = PWMOut(A2)
        self.B1 = PWMOut(B1)
        self.B2 = PWMOut(B2)
        LOGGER.debug('finished setting up PWM pins')
        # setup hall effect switch
        LOGGER.debug(f'setting up hall switch {hall}')
        self.hall = DigitalInOut(hall)
        self.hall.direction = Direction.INPUT
        LOGGER.debug(f'finished setting up hall switch')

        # setup stepper motor
        self.motor = StepperMotor(self.A1, self.A2, self.B1, self.B2, microsteps=self.microsteps)
        LOGGER.debug('finished setting up stepper motor')

        # process variables
        self.position = 0
        self.error = 0
        self.slewing = False
        self.homed = False

        self.set_rpm(Drive.RPM)
        LOGGER.info(f'initialized drive, {Drive.RPM = :.5f} {self.homed = }')

    def __del__(self):
        self.motor.release()

    def _step(self, direction, style, delay):
        self.motor.onestep(direction=direction, style=style)
        sleep(delay)

    def _trigger(self) -> bool:
        return not self.hall.value

    def rpm(self):
        steps = (360 / Drive.STEP_ANGLE) * (1 / self.ratio)
        return 60 / (steps * self.delay)

    def set_rpm(self, rpm):
        LOGGER.debug(f'changing rpm from {self.rpm():.5f} to {rpm:.5f}')
        steps = (360 / Drive.STEP_ANGLE) * (1 / self.ratio)
        self.delay = 60 / (steps * rpm)
        LOGGER.info(f'rpm set to {rpm:.5f}')

    def step_forward(self, delay=None):
        self._step(BACKWARD, SINGLE, self.delay if delay is None else delay)

    def step_backward(self, delay=None):
        self._step(FORWARD, SINGLE, self.delay if delay is None else delay)

    def dstep_forward(self, delay=None):
        self._step(BACKWARD, DOUBLE, self.delay if delay is None else delay)

    def dstep_backward(self, delay=None):
        self._step(FORWARD, DOUBLE, self.delay if delay is None else delay)

    def mstep_forward(self, delay=None):
        self._step(BACKWARD, MICROSTEP, self.delay if delay is None else delay)

    def mstep_backward(self, delay=None):
        self._step(FORWARD, MICROSTEP, self.delay if delay is None else delay)

    def home(self, hold=False):
        LOGGER.debug('starting homing procedure')
        self.set_rpm(self.rpm() / 2)  # slow down during homing

        if self._trigger():
            LOGGER.debug('already in home region, backing up')
            while self._trigger():
                self.mstep_backward()
                self.mstep_backward()

        LOGGER.debug('seeking home region')
        while not self._trigger():
            self.mstep_forward()
        # on the first step where trigger was measured True

        LOGGER.debug('measuring the width of the home region')

        width = 0
        while self._trigger():
            width += 1
            self.mstep_forward()

        LOGGER.debug(f'{width = } steps')

        center = width // 2
        for _ in range(center):
            self.mstep_backward()

        LOGGER.debug(f'centered within home region at step {center}')

        # ok we are home
        self.position = 0  # 
        self.homed = True
        if not hold:
            self.motor.release()
        self.set_rpm(self.rpm() * 2)  # speed back up now that homing is done
        LOGGER.info('drive homed')

    def _demand_to_step(self, D) -> tuple[int, float]:
        '''Convert a demand angle D to an integer number steps and a set point error. '''
        quotient = D / self.theta
        n_a = ceil(quotient)
        n_b = floor(quotient)

        error_a = D - n_a * self.theta
        error_b = D - n_b * self.theta

        if abs(error_a) < abs(error_b):
            return n_a, error_a
        return n_b, error_b

    def _distance(self, D):
        '''Computation of angular distance. '''
        return D - self.position


    def slew(self, D, hold=False):
        '''
        Slew the drive to angle D corrected with a compass
        0 deg is North
        90 deg is East
        180 deg is South
        270 deg is West

        (should compass north be read each slew or should the north position when it was homed be used?)
        '''
        LOGGER.info(f'slewing to {D:.5f}, current {self.position = :.5f}')
        if (abs(D) >= 360):
            D = D % 360
        self.slewing = True
        distance = self._distance(D)
        LOGGER.debug(f'calculated change of position, {distance = :.5f}')
        if distance > 0:
            # slew forward
            steps, error = self._demand_to_step(abs(distance))
            LOGGER.debug(f'steps to move {steps}, positional error {error:.5f}')
            self.position += steps * self.theta
            self.error += error
            for _ in range(steps):
                self.mstep_forward()
        else:
            # slew backwards
            steps, error = self._demand_to_step(abs(distance))
            LOGGER.debug(f'steps to move {steps}, positional error {error:.5f}')
            self.position -= steps * self.theta
            self.error += error
            for _ in range(steps):
                self.mstep_backward()
        self.slewing = False
        sleep(self.delay)
        if not hold:
            self.motor.release()
        LOGGER.info(f'slew complete, {self.position = :.5f} {self.error:.5f}')

class AzDrive(Drive):
    def __init__(self, compass, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.compass = compass

    def home(self, *args, **kwargs):
        Drive.home(self, *args, **kwargs)
        self.north = self.compass.direction()

    def _distance(self, D):
        '''Compute angular distance but apply compass correction. '''
        return (D + self.north) - self.position
