# from collect import raw_data_from_file, SDR
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from numpy import ndarray, array
from scipy.signal import welch, get_window
import logging


logging.basicConfig(level=logging.DEBUG)
logging.getLogger('h5py').setLevel(logging.WARNING)
# logging.getLogger('matplotlib').setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)
FIG_SIZE = (25, 8)


def plot_complex_timeseries(series: array, show: bool = True,
                            fname: None | str | Path = None):
    fig, axs = plt.subplots(2, figsize=FIG_SIZE, sharex=True)
    fig.suptitle('Normed IQ Time-series')
    fig.supxlabel('step')
    fig.supylabel('')

    axs[0].set_title('Real')
    axs[0].plot(series.real, color='tab:blue')
    axs[0].grid()

    axs[1].set_title('Imaginary')
    axs[1].plot(series.imag, color='tab:green')
    axs[1].grid()
    plt.tight_layout()
    if fname:
        _fname = f'{fname}.png'
        plt.savefig(_fname)
        LOGGER.info(f'wrote out {_fname}')
    if show:
        plt.show()


def plot_magnitude_phase_timeseries(series: array, show: bool = True,
                                    fname: None | str | Path = None):
    fig, axs = plt.subplots(2, figsize=FIG_SIZE, sharex=True)
    fig.suptitle('Magnitude & Phase Time-series')
    fig.supxlabel('time')

    axs[0].set_title('Magnitude')
    axs[0].plot(np.abs(series), color='tab:blue')
    axs[0].set_ylabel('Normed Magnitude')
    axs[0].grid()

    axs[1].set_title('Phase Angle')
    axs[1].plot(np.angle(series) * 180 / np.pi, color='tab:green')
    axs[1].set_ylabel('Angle (degree)')
    axs[1].grid()

    plt.tight_layout()
    if fname:
        _fname = f'{fname}.png'
        plt.savefig(_fname)
        LOGGER.info(f'wrote out {_fname}')
    if show:
        plt.show()


def plot_magnitude_histogram(series: array, show: bool = True,
                             fname: None | str | Path = None):
    plt.figure(figsize=FIG_SIZE)
    plt.title('IQ Magnitude Histogram')
    plt.xlabel('Normed Magnitude')
    plt.ylabel('Density')
    plt.hist(np.abs(series), bins=100, density=True)
    plt.grid()
    plt.tight_layout()
    if fname:
        _fname = f'{fname}.png'
        plt.savefig(_fname)
        LOGGER.info(f'wrote out {_fname}')
    if show:
        plt.show()


# def plot_spectrogram(n, N):
#     '''Short-Time Fourier Transform (STFT). '''
#     # looks like garbage, need to read up on this

#     f, t, Sxx = spectrogram(data[n], fs=1/sdr.sample_rate, nperseg=N)
#     plt.figure(figsize=FIG_SIZE)
#     plt.pcolormesh(t, f, 10 * np.log10(Sxx), shading='auto')
#     plt.xlabel("Time (s)")
#     plt.ylabel("Frequency (Hz)")
#     plt.title("Spectrogram of IQ Data")
#     plt.colorbar(label="Power (dB)")
#     plt.tight_layout()
#     plt.show()


def plot_spectrum(series: array, meta: dict, nbins: int = 8192, N_SEG_LIM=2048,
                  show: bool = True, fname: None | Path | str = None):
    window = 'hann'
    if nbins < N_SEG_LIM:
        nperseg = nbins
    else:
        nperseg = N_SEG_LIM

    freqs, Pxx = welch(series, fs=meta['sample_rate'], nperseg=nperseg,
                       nfft=nbins, noverlap=0, scaling='spectrum',
                       window=window, detrend=False, return_onesided=False)

    freqs = np.fft.fftshift(freqs)
    Pxx = np.fft.fftshift(Pxx)

    win = get_window(window, nperseg)
    Pxx_hz = Pxx * ((win.sum()**2) / (win*win).sum()) / meta['sample_rate']
    Pxx_db_hz = 10. * np.log10(Pxx_hz)

    # Shift frequency spectra back to the intended range
    freqs = (freqs + meta['center_freq']) / 1e6
    plt.figure(figsize=FIG_SIZE)
    plt.title('Power Spectral Density Estimate')
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Power Spectral Density (dB/Hz)')
    plt.plot(freqs, Pxx_db_hz)
    plt.grid()
    plt.tight_layout()
    if fname:
        _fname = f'{fname}'
        plt.savefig(_fname)
        LOGGER.info(f'wrote out {_fname}')
    if show:
        plt.show()


def spectrum_integration(data: ndarray, meta: dict, nbins: int = 8192,
                         N_SEG_LIM=2048, show: bool = True,
                         fname: None | Path | str = None):
    window = 'hann'
    if nbins < N_SEG_LIM:
        nperseg = nbins
    else:
        nperseg = N_SEG_LIM

    freqs = np.zeros(nbins)
    Pxx_total = np.zeros(nbins)

    for iq in data:
        # compensate for DC spike
        iq = (iq.real - iq.real.mean()) + (1j * (iq.imag - iq.imag.mean()))
        freqs, p_xx = welch(iq, fs=meta['sample_rate'], nperseg=nperseg,
                            nfft=nbins, noverlap=0, scaling='spectrum',
                            window=window, detrend=False, return_onesided=False)
        Pxx_total += p_xx

    freqs = np.fft.fftshift(freqs)
    Pxx_total = np.fft.fftshift(Pxx_total)

    P_avg = Pxx_total / len(data)
    win = get_window(window, nperseg)
    P_avg_hz = P_avg * ((win.sum()**2) / (win*win).sum()) / meta['sample_rate']
    P_avg_db_hz = 10. * np.log10(P_avg_hz)

    # Shift frequency spectra back to the intended range
    freqs = (freqs + meta['center_freq']) / 1e6
    plt.figure(figsize=FIG_SIZE)
    plt.title('Power Spectral Density Estimate')
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Power Spectral Density (dB/Hz)')
    plt.plot(freqs, P_avg_db_hz)
    plt.grid()
    plt.tight_layout()
    if fname:
        _fname = f'{fname}.png'
        plt.savefig(_fname)
        LOGGER.info(f'wrote out {_fname}')
    if show:
        plt.show()


if __name__ == '__main__':
    import collect
    from argparse import ArgumentParser

    SPECTRA_DIR = Path('spectra')
    reducers = ['iq_timeseries', 'magnitude_phase_timeseries',
                'magnitude_histogram', 'spectrum']

    parser = ArgumentParser()
    parser.add_argument('reducer', type=str,
                        help='In which way would you like to reduce the data?')
    parser.add_argument('data', type=Path, help='path to h5py data file')
    parser.add_argument('--show', action='store_true', default=False,
                        help='pass to open plot interactively')
    # parser.add_argument('--fname', default=None,
    #                     help='optional path to write plot to')
    parser.add_argument('--save', default=False, action='store_true',
                        help='pass this flag to write to file')
    parser.add_argument('--n', default=None, type=int,
                        help='select a row in a dataset, otherwise mean of dataset')
    parser.add_argument('--spectra', default=SPECTRA_DIR, type=Path, 
                        help=f'define the directory to store spectra in, default {SPECTRA_DIR}')

    args = parser.parse_args()
    if not (args.spectra.exists() and args.spectra.is_dir()):
        args.spectra.mkdir(parents=True)
        LOGGER.info(f'created {args.spectra} to store spectral images')

    fname = None
    if args.save:
        fname = args.spectra / args.data.stem

    match args.reducer:
        case 'iq_timeseries':
            LOGGER.debug('iq_timeseries reduction')
            data, _ = collect.read_h5py(args.data)
            if args.n:
                plot_complex_timeseries(data[args.n], args.show, fname)
            else:
                plot_complex_timeseries(data.mean(axis=0), args.show, fname)

        case 'magnitude_phase_timeseries':
            LOGGER.debug('magnitude_phase_timeseries reduction')
            data, _ = collect.read_h5py(args.data)
            if args.n:
                plot_magnitude_phase_timeseries(data[args.n], args.show, fname)
            else:
                plot_magnitude_phase_timeseries(data.mean(axis=0), args.show, fname)

        case 'magnitude_histogram':
            LOGGER.debug('magnitude_phase_timeseries reduction')
            data, _ = collect.read_h5py(args.data)
            if args.n:
                plot_magnitude_histogram(data[args.n], args.show, fname)
            else:
                plot_magnitude_histogram(data.mean(axis=0), args.show, fname)

        case 'spectrum':
            LOGGER.debug('spectrum reduction')
            data, meta = collect.read_h5py(args.data)
            if args.n:
                LOGGER.info('integrating 1 row')
                plot_spectrum(data[args.n], meta, show=args.show, fname=fname)
            else:
                LOGGER.info('integrating the data set')
                spectrum_integration(data, meta, show=args.show, fname=fname)
        case _:
            LOGGER.info(f'Reducers: {reducers}')
