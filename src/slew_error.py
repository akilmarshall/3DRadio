from math import floor, ceil
import logging
import matplotlib.pyplot as plt
import numpy as np


# logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def theta(step_rotation=1.8, microsteps=1, ratio=29/149):
    return (step_rotation / microsteps) * ratio


def solve(theta, D):
    '''
    Given a theta (angular movement per step) and demand angle D, compute the n that minimizes

                                |D - n * theta|

    returns (n, error)
    '''
    n_a = floor(D / theta)
    n_b = ceil(D / theta)

    LOGGER.info(f'candidates: {n_a} {n_b}')

    error_a = D - n_a * theta
    error_b = D - n_b * theta

    LOGGER.info(f'errors: {error_a:.4f} {error_b:.4f}')

    if abs(error_a) < abs(error_b):
        return n_a, error_a

    return n_b, error_b



def plot_error(theta, step_size):
    '''
    Domain is the points that satisfy: 0 <= step_size * i < 360 for positive integer i.
    compute the error across the domain and make a plot.
    '''
    steps = np.arange(0, 360, step_size)
    error = list()

    for D in steps:
        error.append(solve(theta, D)[1])

    plt.grid(True)
    # plt.tight_layout()
    plt.title(f'Setpoint Error for a given Demand Angle\nMove Resolution: ~{theta:0.5f} Demand Resolution: {step_size}')
    plt.xlabel('Demand Angle (degrees)')
    plt.ylabel('Error (degrees)')
    plt.scatter(steps, error)
    plt.show()
