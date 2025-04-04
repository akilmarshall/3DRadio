from dataclasses import dataclass
from math import sqrt
from numpy import ndarray
from pathlib import Path
from rtlsdr import RtlSdr
from typing import Self
import json
import logging
import numpy as np
import h5py
from itertools import product
from enum import Enum
import threading

from datetime import datetime, timedelta, timezone


logging.basicConfig(level=logging.INFO)
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)


@dataclass
class ConfSDR:
    gain: float # gain in dB
    # bandwidth: int = 0           # bandwidth in Hz
    center_freq: int = 1420.4e6  # center frequency in Hz
    # freq_correction: int = 0     # frequency correction in ppm
    sample_rate: int = 2.85e6    # sample rate in Hz (f_s)
    n: int = 1024
    # n: int = 2048                # fft width low resolution
    # n: int = 20480               # fft width medium resolution
    # n: int = 204800              # fft width high resolution
    super_sample: int = 2
    serial_number: str = '00000001'
    # sdr: None | RtlSdr = None    # sdr

    def T(self):
        return 1 / self.sample_rate

    def tau(self):
        return self.T() * self.n

    def frequency_resolution(self):
        return self.sample_rate / self.n

    def signal_duration(self):
        return self.n * self.super_sample / self.super_sample

    def metadata(self):
        '''
        Return a dict describing the SDR configuration (user provided)
        '''

        meta = {
                'set': {
                    # 'bandwidth': self.bandwidth,
                    'center_freq': self.center_freq,
                    # 'freq_correction': self.freq_correction,
                    'gain': self.gain,
                    'sample_rate': self.sample_rate,
                    'n': self.n,
                    'super_sample': self.super_sample,
                    }
                }

        return meta


class Load(str, Enum):
    sky = 'sky'
    zenith = 'zenith'
    cold = 'cold'
    hot = 'hot'


@dataclass
class ConfTelescope:
    f: int # focal distance in mm
    D: int # diameter of the reflector dish in mm
    load: Load
    name: str = '' # optional name of the telescope
    note: str = '' # optional notes for the telescope
    signal_sn: str = '00000010'  # serial number of the SDR connected to the antenna
    reference_sn: str = '00000011'  # serial number of the SDR connected 50ohm termination

    def fD(self):
        return self.f / self.D

    def metadata(self):
        '''Return a dict describing the Telescope configuration (user provided). '''

        meta = {
                'f': self.f,
                'D': self.D,
                'name': self.name,
                'note': self.note,
                'load': self.load.value,
                'signal_sn': self.signal_sn,
                'reference_sn': self.reference_sn
                }

        return meta


@dataclass
class ConfGeneral:
    latitude: float
    longitude: float
    datetime: datetime
    row: int
    note: str = ''

    def initialize(self, offset: int = -10):
        '''Set the timestamp. '''

        offset = timedelta(hours=offset)
        tz = timezone(offset)
        self.datetime = datetime.now(tz)

    def timestamp(self):
        return f'{self.datetime.year}{self.datetime.month:02}{self.datetime.day:02}.{self.datetime.hour:02}{self.datetime.minute:02}'


class SDR(ConfSDR):
    def configure(self):
        LOGGER.info(f'configuring RTL-SDR Blog V4 {self.serial_number=}')
        # LOGGER.info(f'\t{self.bandwidth=} Hz')
        LOGGER.info(f'\t{self.center_freq=} Hz')
        # LOGGER.info(f'\t{self.gain=} dB')
        LOGGER.info(f'\t~{self.sample_rate=} Hz')
        LOGGER.info(f'\t{self.n=}')
        LOGGER.info(f'\t~{self.frequency_resolution()=} Hz')
        LOGGER.info(f'\t{self.super_sample=}')
        # if self.sdr is None:
        LOGGER.info(f'initializing RTL-SDR Blog V4 {self.serial_number=}')
        self.sdr = RtlSdr(serial_number=self.serial_number)

        # self.sdr.bandwidth = self.bandwidth
        self.sdr.center_freq = self.center_freq
        self.sdr.gain = self.gain
        self.sdr.sample_rate = self.sample_rate
        LOGGER.info(f'{self.sdr.get_gain()=}')
        LOGGER.info(f'{self.sdr.get_bandwidth()=}')
        LOGGER.info(f'{self.sdr.get_sample_rate()=}')

    def __del__(self):
        if self.sdr is not None:
            self.sdr.close()
            LOGGER.info(f'closed SDR RTL V4 Blog {self.serial_number=}')

    def integrate(self):
        if self.sdr is None:
            LOGGER.warning('please configure the SDR')
            return
        N = self.n * self.super_sample
        LOGGER.debug(f'reading {N} samples')
        return self.sdr.read_samples(num_samples=self.n * self.super_sample)

    def integrateN(self, N: int, buffer: ndarray) -> None:
        lost_integrations = 0
        if self.sdr is None:
            LOGGER.warning('please configure the SDR')
            return None
        else:
            data_set = list()
            LOGGER.info(f'starting integration {N} rows')
            for i in range(N):
                LOGGER.debug(f'row {i}')
                try:
                    data_set.append(self.integrate())
                except IOError as e:
                    LOGGER.exception(e)
                    lost_integrations += 1
            LOGGER.info('complete')
            if lost_integrations > 0:
                LOGGER.info(f'{lost_integrations} integrations lost')
            buffer[:] = np.vstack(data_set)


def raw_data_to_file(data: ndarray, fname: Path | str):
    '''write uncompressed npy file. '''
    LOGGER.warning('deprecated')
    np.save(fname, data)
    LOGGER.info(f'wrote data to {fname}')


def write_h5py(data: ndarray, meta: dict, fname: Path | str):
    LOGGER.warning('deprecated')
    LOGGER.info(f'compressing and writing data to {fname}.h5')
    with h5py.File(f'{fname}.h5', 'w') as f:
        f.create_dataset('IQ',
                         data=data,
                         compression='gzip',
                         compression_opts=5)
        LOGGER.info('adding in metadata')
        for key in meta['set']:
            val = meta['set'][key]
            LOGGER.debug(f'{key} = {val}')
            f['IQ'].attrs[key] = val


def raw_data_from_file(fname: Path | str) -> ndarray:
    '''load npy file. '''
    LOGGER.warning('deprecated')
    LOGGER.info(f'loading data from {fname}')
    return np.load(fname)


def read_h5py(fname: Path | str) -> tuple[ndarray, dict]:
    LOGGER.warning('deprecated')
    LOGGER.info(f'loading {fname}')
    with h5py.File(fname, 'r') as f:
        return f['IQ'][:], dict(f['IQ'].attrs)


def collect(freqs: list[float], sample_rates: list[float], ns: list[int],
            rows: list[int], super_samples: list[int],
            genConf: ConfGeneral, teleConf: ConfTelescope,
            fname: str | Path):
    '''
    The provided list parameters overide the associate value in the Conf
    structures. These iterations form the observation, 
    they are performed in sequence in a cartesian product
    freq x sample rate x n x row x super_sample
    '''
    with h5py.File(f'{fname}.h5', 'w') as file:
        genConf.initialize()
        LOGGER.debug('writing out General configuration')
        file.attrs['latitude'] = genConf.latitude
        file.attrs['longitude'] = genConf.longitude
        file.attrs['datetime'] = genConf.datetime.isoformat()
        file.attrs['row'] = rows
        file.attrs['note'] = genConf.note
        LOGGER.debug('writing out Telescope configuration')
        file.attrs['f'] = teleConf.f
        file.attrs['D'] = teleConf.D
        file.attrs['name'] = teleConf.name
        file.attrs['telescope-note'] = teleConf.note
        file.attrs['load'] = teleConf.load.value
        LOGGER.debug('writing out SDR configuration')
        file.attrs['frequency'] = freqs
        file.attrs['sample_rate'] = sample_rates
        file.attrs['n'] = ns
        file.attrs['super_sample'] = super_samples
        # make the data group
        offset = timedelta(hours=-10)
        tz = timezone(offset)
        for i, (freq, sr, n, row, ss) in enumerate(product(freqs, sample_rates, ns, rows, super_samples)):
            LOGGER.info(f'Integrating: {freq=} {sr=} {n=} {row=} {ss=}')
            sdr = SDR(center_freq=freq, gain='auto', sample_rate=sr, n=n,
                      super_sample=ss, serial_number=teleConf.signal_sn)
            sdr.configure()
            reference = SDR(center_freq=freq, gain='auto', sample_rate=sr, n=n,
                            super_sample=ss, serial_number=teleConf.reference_sn)
            reference.configure()

            # setup data buffers
            width = sdr.n * sdr.super_sample
            data_sig = np.zeros((row, width), dtype=np.complex128)
            data_ref = np.zeros((row, width), dtype=np.complex128)

            thread_data = threading.Thread(target=sdr.integrateN, args=(row, data_sig))
            thread_reference = threading.Thread(target=reference.integrateN, args=(row, data_ref))

            start = datetime.now(tz)
            thread_data.start()
            thread_reference.start()

            thread_data.join()
            thread_reference.join()
            end = datetime.now(tz)

            group = file.create_group(f'data/{i}')
            group.create_dataset('IQ', data=data_sig, compression='gzip', compression_opts=5)
            group.create_dataset('reference', data=data_ref, compression='gzip', compression_opts=5)

            # write meta data for the data set
            group.attrs['frequency'] = freq
            group.attrs['sample_rate'] = sr
            group.attrs['n'] = n
            group.attrs['row'] = row
            group.attrs['super_sample'] = ss
            group.attrs['obs_start_time'] = start.isoformat()
            group.attrs['obs_end_time'] = end.isoformat()

        LOGGER.info(f'integrated {i + 1} times')


if __name__ == '__main__':
    from argparse import ArgumentParser

    ROWS = [1000]
    freqs = [1420.4e6]
    # gains = [1, 49.8]
    sample_rates = [2.4e6, 2.6e6, 2.85e6, 3.0e6]
    ns = [1024, 2048]
    rows = [1000, 2000]
    super_samples = [2]
    # SDR_CONF_DIR = Path('sdr_conf-test')
    DATA_DIR = Path('data')

    parser = ArgumentParser()
    parser.add_argument('--center_freq', '-f', default=freqs, type=float,
                        nargs='+',
                        help=f'center frequency, default {freqs} Hz')
    parser.add_argument('--gain', '-g', type=float, default=20,
                        help='gain in dB, valid values in [1, 49.8]')
    parser.add_argument('--sample_rate', '-s', default=sample_rates, type=float,
                        nargs='+',
                        help=f'sample rate, default {sample_rates} Hz')
    parser.add_argument('--n', '-n', default=ns, type=int,
                        nargs='+',
                        help=f'how many samples per call to the ADC (powers of 2 only!), default {ns}')
    parser.add_argument('--rows', '-r', default=ROWS, type=int,
                        nargs='+',
                        help=f'how many rows of data to take, default {ROWS}')
    parser.add_argument('--super_sample', '-S', default=super_samples, type=int,
                        nargs='+',
                        help=f'multiplies the sample width, default {super_samples}')
    parser.add_argument('--data', default=DATA_DIR, type=Path,
                        help=f'define the directory to store the data files in, default {DATA_DIR}')
    parser.add_argument('--note', help='note describing the dataset')
    parser.add_argument('--tele_note', help='note describing the telescope')
    parser.add_argument('--tele_name', help='name of the telescope and/or configuration')

    args = parser.parse_args()

    if not (args.data.exists() and args.data.is_dir()):
        args.data.mkdir()
        LOGGER.info(f'created {args.data} for storing data files')

    genConf = ConfGeneral(0, 0, 0, args.rows[0], args.note)
    genConf.initialize()
    teleConf = ConfTelescope(216, 540, Load.sky, args.tele_name, args.tele_note)
    collect(args.center_freq,
            args.sample_rate,
            args.n,
            args.rows,
            args.super_sample,
            genConf,
            teleConf,
            args.data / genConf.timestamp())
