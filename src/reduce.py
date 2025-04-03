# from collect import raw_data_from_file, SDR
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from numpy import ndarray, array
from scipy.signal import welch, get_window, correlate
import logging
# from fpdf import FPDF
import h5py
# from PIL import Image


logging.basicConfig(level=logging.DEBUG)
logging.getLogger('h5py').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)
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

    plt.close()


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

    plt.close()


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

    plt.close()


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


def plot_spectrum(series: array, attrs: dict, nbins: int = 8192, N_SEG_LIM=2048,
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
        _fname = f'{fname}.png'
        plt.savefig(_fname)
        LOGGER.info(f'wrote out {_fname}')
    if show:
        plt.show()

    plt.close()


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
    freqs = (freqs + meta['frequency']) / 1e6
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
    plt.close()


def autocorrelate(data: ndarray, meta: dict, show: bool = True,
                  fname: None | Path | str = None):
    ACF = list()
    for sample in data:
        acf = correlate(sample, sample, mode='full', method='fft')
        # Normalize the autocorrelation function
        acf /= np.max(acf)
        ACF.append(acf)

    # Create a time lag vector for plotting
    lags = np.arange(0, len(data[0])) / meta['sample_rate']

    ACF = np.vstack(ACF)
    # average the autocorrelation functions
    acf = np.sum(ACF, axis=0) / len(ACF)

    # Plot the autocorrelation function
    import matplotlib.pyplot as plt
    plt.figure(figsize=FIG_SIZE)
    plt.title('Mean Autocorrelation Function')
    plt.xlabel('Lag (seconds?)')
    plt.ylim(-0.02, 0.02)
    # plt.ylabel('Autocorrelation')
    plt.plot(lags, acf[len(lags) - 1:])
    plt.grid(True)
    if fname:
        _fname = f'{fname}.png'
        plt.savefig(_fname)
        LOGGER.info(f'wrote out {_fname}')
    if show:
        plt.show()

    plt.close()


if __name__ == '__main__':
    from argparse import ArgumentParser

    PRODUCTS_DIR = Path('reduction-products')
    # all
    reducers = ['iq_timeseries', 'magnitude_phase_timeseries',
                'magnitude_histogram', 'spectrum', 'autocorrelate']
    # spectral
    # reducers = ['spectrum', 'autocorrelate']

    parser = ArgumentParser()
    parser.add_argument('--reducer', '-r', type=str, nargs='+',
                        help='In which way would you like to reduce the data?')
    parser.add_argument('--data', '-d', type=Path, help='path to h5py data file')
    parser.add_argument('--show', action='store_true', default=False,
                        help='pass to open plot interactively')
    parser.add_argument('--save', default=False, action='store_true',
                        help='pass this flag to write to file')
    parser.add_argument('--n', default=None, type=int,
                        help='select a row in a dataset, otherwise mean of dataset')
    parser.add_argument('--products', default=PRODUCTS_DIR, type=Path, 
                        help=f'define the directory to store reduction prodcuts in, default {PRODUCTS_DIR}')

    args = parser.parse_args()
    if not (args.products.exists() and args.products.is_dir()):
        args.products.mkdir(parents=True)
        LOGGER.info(f'created {args.products} to store reduction products')

    fname = None
    if args.save:
        fname = args.products / args.data.stem

    # data, meta = collect.read_h5py(args.data)
    with h5py.File(args.data, 'r') as file:
        def reduce(option):
            match option:
                case 'iq_timeseries':
                    LOGGER.info('IQ Timeseries Reduction')
                    if args.n:
                        # TODO just plot the nth
                        pass
                    else:
                        for i in range(len(file['data'])):
                            data = file[f'data/{i}/IQ'][:]
                            ref = file[f'data/{i}/reference'][:]
                            corrected = data - ref
                            plot_complex_timeseries(
                                    data.mean(axis=0),
                                    args.show,
                                    args.products / f'{args.data.stem}-{option}-{i}-signal')
                            plot_complex_timeseries(
                                    ref.mean(axis=0),
                                    args.show,
                                    args.products / f'{args.data.stem}-{option}-{i}-reference')
                            plot_complex_timeseries(
                                    corrected.mean(axis=0),
                                    args.show,
                                    args.products / f'{args.data.stem}-{option}-{i}-corrected')

                case 'magnitude_phase_timeseries':
                    LOGGER.info('Magnitude Phase Timeseries Reduction')
                    if args.n:
                        # TODO just plot the nth
                        pass
                    else:
                        for i in range(len(file['data'])):
                            data = file[f'data/{i}/IQ'][:]
                            ref = file[f'data/{i}/reference'][:]
                            corrected = data - ref
                            plot_magnitude_phase_timeseries(
                                    data.mean(axis=0),
                                    args.show,
                                    args.products / f'{args.data.stem}-{option}-{i}-signal')
                            plot_magnitude_phase_timeseries(
                                    ref.mean(axis=0),
                                    args.show,
                                    args.products / f'{args.data.stem}-{option}-{i}-reference')
                            plot_magnitude_phase_timeseries(
                                    corrected.mean(axis=0),
                                    args.show,
                                    args.products / f'{args.data.stem}-{option}-{i}-corrected')

                case 'magnitude_histogram':
                    LOGGER.info('Magnitude Phase Timeseries Reduction')
                    if args.n:
                        # plot_magnitude_histogram(data[args.n], args.show, fname)
                        pass
                    else:
                        for i in range(len(file['data'])):
                            data = file[f'data/{i}/IQ'][:]
                            ref = file[f'data/{i}/reference'][:]
                            corrected = data - ref
                            plot_magnitude_histogram(
                                    data.mean(axis=0),
                                    args.show,
                                    args.products / f'{args.data.stem}-{option}-{i}-signal')
                            plot_magnitude_histogram(
                                    ref.mean(axis=0),
                                    args.show,
                                    args.products / f'{args.data.stem}-{option}-{i}-reference')
                            plot_magnitude_histogram(
                                    corrected.mean(axis=0),
                                    args.show,
                                    args.products / f'{args.data.stem}-{option}-{i}-corrected')

                case 'spectrum':
                    LOGGER.info('Spectrum Reduction')
                    if args.n:
                        # LOGGER.info('integrating 1 row')
                        # plot_spectrum(data[args.n], meta, show=args.show, fname=fname)
                        pass
                    else:
                        LOGGER.debug('integrating the data set')
                        for i in range(len(file['data'])):
                            group = file[f'data/{i}']
                            data = group['IQ'][:]
                            ref = group['reference'][:]
                            corrected = data - ref
                            spectrum_integration(
                                    data,
                                    group.attrs,
                                    show=args.show,
                                    fname=args.products / f'{args.data.stem}-{option}-{i}-signal')
                            spectrum_integration(
                                    ref,
                                    group.attrs,
                                    show=args.show,
                                    fname=args.products / f'{args.data.stem}-{option}-{i}-reference')
                            spectrum_integration(
                                    corrected,
                                    group.attrs,
                                    show=args.show,
                                    fname=args.products / f'{args.data.stem}-{option}-{i}-corrected')
                case 'autocorrelate':
                    LOGGER.info('Autocorrelation Function Reduction')
                    for i in range(len(file['data'])):
                        group = file[f'data/{i}']
                        data = group['IQ'][:]
                        ref = group['reference'][:]
                        corrected = data - ref
                        autocorrelate(
                                data,
                                group.attrs,
                                show=args.show,
                                fname=args.products / f'{args.data.stem}-{option}-{i}-signal')
                        autocorrelate(
                                ref,
                                group.attrs,
                                show=args.show,
                                fname=args.products / f'{args.data.stem}-{option}-{i}-reference')
                        autocorrelate(
                                corrected,
                                group.attrs,
                                show=args.show,
                                fname=args.products / f'{args.data.stem}-{option}-{i}-corrected')
                case _:
                    LOGGER.info(f'Reducers: {reducers}')

        for reducer in args.reducer:
            if reducer == 'all':
                # class PDF(FPDF):
                #     def header(self):
                #         self.set_font('Arial', 'B', 14)
                #         self.cell(0, 10, args.data.stem, ln=True, align='C')

                # pdf = PDF()
                # pdf.add_page()
                # pdf.set_font('Arial', 'B', 10)
                # for i, key in enumerate(file.attrs.keys()):
                #     val = file.attrs[key]
                #     pdf.cell(10, 10, f'{key} = {val}', 0, 1)

                for reducer in reducers:
                    FIG_SIZE = (6, 5)
                    reduce(reducer)
                    LOGGER.info('pdf output disabled until pandoc upgrade')
                    '''
                    for i in range(len(file['data'])):
                        pdf.add_page()
                        pdf.set_font('Arial', 'B', 14)
                        img_signal = args.products / f'{args.data.stem}-{reducer}-{i}-signal.png'
                        img_reference = args.products / f'{args.data.stem}-{reducer}-{i}-reference.png'
                        LOGGER.debug(img_signal, img_reference)
                        attrs = "\n".join(f"{k} = {v}" for k, v in file[f'/data/{i}'].attrs.items())
                        pdf.multi_cell(150, 8, attrs, align='L')
                        pdf.image(img_signal.as_posix(), 0, 80)
                        pdf.image(img_reference.as_posix(), 0, 80)

                pdf.output(args.products / f'report-{args.data.stem}.pdf')
                '''
            else:
                reduce(reducer)
