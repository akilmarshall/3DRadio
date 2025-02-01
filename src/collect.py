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

from datetime import datetime, timedelta


logging.basicConfig(level=logging.INFO)
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)


@dataclass
class Conf:
    # bandwidth: int = 0           # bandwidth in Hz
    center_freq: int = 1420.4e6  # center frequency in Hz
    # freq_correction: int = 0     # frequency correction in ppm
    gain: str | float = 'auto'   # gain in dB
    sample_rate: int = 2.85e6    # sample rate in Hz (f_s)
    n: int = 1024
    # n: int = 2048                # fft width low resolution
    # n: int = 20480               # fft width medium resolution
    # n: int = 204800              # fft width high resolution
    super_sample: int = 2
    sdr: None | RtlSdr = None    # sdr

    def T(self):
        return 1 / self.sample_rate

    def tau(self):
        return self.T() * self.n

    def frequency_resolution(self):
        return self.sample_rate / self.n

    def signal_duration(self):
        return self.n * self.super_sample / self.super_sample


class SDR(Conf):
    def configure(self):
        LOGGER.info('configuring RTL-SDR Blog V4')
        # LOGGER.info(f'\t{self.bandwidth=} Hz')
        LOGGER.info(f'\t{self.center_freq=} Hz')
        # LOGGER.info(f'\t{self.gain=} dB')
        LOGGER.info(f'\t~{self.sample_rate=} Hz')
        LOGGER.info(f'\t{self.n=}')
        LOGGER.info(f'\t~{self.frequency_resolution()=} Hz')
        LOGGER.info(f'\t{self.super_sample=}')
        if self.sdr is None:
            LOGGER.info('initializing RTL-SDR Blog V4')
            self.sdr = RtlSdr()

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
            LOGGER.info('closed SDR RTL V4 Blog')

    def metadata(self):
        '''
        Return a dict describing the SDR configuration (user provided)
        and the real configuration as reported by the SDR.
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
        if self.sdr:
            meta['real'] = {
                    'bandwidth': self.sdr.get_bandwidth(),
                    'center_freq': self.sdr.get_center_freq(),
                    'freq_correction': self.sdr.get_freq_correction(),
                    'gain': self.sdr.get_gain(),
                    'sample_rate': self.sdr.get_sample_rate(),
                    }
        return meta

    def to_file(self, fname: Path | str):
        with open(fname, 'w') as f:
            json.dump(self.metadata(), f, indent=4)

        LOGGER.info(f'wrote sdr metadata to {fname}')

    @staticmethod
    def from_file(fname: Path | str) -> Self | None:
        with open(fname, 'r') as f:
            loaded = json.load(f)
        sdr = SDR()
        if 'set' in loaded:
            setting = loaded['set']
            # sdr.bandwidth = int(setting['bandwidth'])
            sdr.center_freq = int(setting['center_freq'])
            # sdr.freq_correction = int(setting['freq_correction'])
            sdr.gain = setting['gain']
            sdr.sample_rate = int(setting['sample_rate'])
            sdr.n = int(setting['n'])
            sdr.super_sample = int(setting['super_sample'])
        else:
            LOGGER.warning(f'setting data not found in {fname}')
            return None

        LOGGER.info(f'initialized SDR from {fname}')
        return sdr

    def integrate(self):
        if self.sdr is None:
            LOGGER.warning('please configure the SDR')
            return
        N = self.n * self.super_sample
        LOGGER.debug(f'reading {N} samples')
        return self.sdr.read_samples(num_samples=self.n * self.super_sample)

    def integrateN(self, N: int) -> None | ndarray:
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
            return np.vstack(data_set)


def raw_data_to_file(data: ndarray, fname: Path | str):
    '''write uncompressed npy file. '''
    np.save(fname, data)
    LOGGER.info(f'wrote data to {fname}')


def write_h5py(data: ndarray, meta: dict, fname: Path | str):
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
    LOGGER.info(f'loading data from {fname}')
    return np.load(fname)


def read_h5py(fname: Path | str) -> tuple[ndarray, dict]:
    LOGGER.info(f'loading {fname}')
    with h5py.File(fname, 'r') as f:
        return f['IQ'][:], dict(f['IQ'].attrs)


if __name__ == '__main__':
    from argparse import ArgumentParser
    import reduce

    ROWS = 1000
    SDR_CONF_DIR = Path('sdr_conf-test')
    DATA_DIR = Path('data-test')

    conf = Conf()
    parser = ArgumentParser()
    parser.add_argument('--center_freq', '-f', default=conf.center_freq, type=float,
                        help=f'center frequency, default {conf.center_freq:4E} Hz')
    parser.add_argument('--gain', '-g', default=conf.gain,
                        help=f'gain, default {conf.gain} dB')
    parser.add_argument('--sample_rate', '-s', default=conf.sample_rate, type=float,
                        help=f'sample rate, default {conf.sample_rate:4E} Hz')
    parser.add_argument('--n', '-n', default=conf.n, type=int, help=f'How many samples per call to the ADC (powers of 2 only!), default {conf.n}')
    parser.add_argument('--rows', '-r', default=ROWS, type=int, help=f'How many rows of data to take, default {ROWS}')
    parser.add_argument('--super_sample', '-S', default=conf.super_sample, type=int,
                        help=f'Multiplies the sample width, default {conf.super_sample}')
    parser.add_argument('--nosave', default=True, action='store_false',
                        help='Pass this flag to stop a data file from being written')
    parser.add_argument('--show', default=False, action='store_true',
                        help='Pass this flag to show the integrated spectra')
    parser.add_argument('--data', default=DATA_DIR, type=Path,
                        help=f'define the directory to store the data files in, default {DATA_DIR}')
    parser.add_argument('--meta', default=SDR_CONF_DIR, type=Path,
                        help=f'define the directory to store the metadata files in, default {SDR_CONF_DIR}')

    args = parser.parse_args()

    if not (args.data.exists() and args.data.is_dir()):
        args.data.mkdir()
        LOGGER.info(f'created {args.data} for storing data files')

    if not (args.meta.exists() and args.meta.is_dir()):
        args.meta.mkdir()
        LOGGER.info(f'created {args.meta} for storing metadata ')

    sdr = SDR(
            center_freq=args.center_freq,
            gain=args.gain if args.gain == 'auto' else float(args.gain),
            sample_rate=args.sample_rate,
            n=args.n,
            super_sample=args.super_sample)
    sdr.configure()
    now = datetime.now()
    time_stamp = f'{now.year}{now.month:02}{now.day:02}.{now.hour:02}{now.minute:02}'
    start = datetime.now()
    data = sdr.integrateN(args.rows)
    end = datetime.now()
    duration = end - start
    _min, sec = divmod(duration.total_seconds(), 60)
    cs = duration.microseconds // 10000  # Convert microseconds to centiseconds
    LOGGER.info(f'integration duration {int(_min):02}:{int(sec):02}:{cs:02}')
    if args.nosave:
        sdr.to_file(args.meta / time_stamp)
        # raw_data_to_file(data, fname=args.data / time_stamp)
        write_h5py(data, sdr.metadata(), args.data / time_stamp)
    if args.show:
        reduce.spectrum_integration(data, sdr.metadata()['set'], show=True)
