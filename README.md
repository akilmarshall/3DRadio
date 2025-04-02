# Assembly Notes

a washer between the lazy susan and static base is necessary to allow clearance for the bolt heads which attach the azimuth gear to the rotating part of the lazy susan.


# Software

- collect.py
    - control RTL SDR
    - read/write configuration from file
    - produce IQ data sets (np.ndarray)
    - write compressed data sets to file (h5)
- reduce.py
    - read compressed data sets from file (h5) 
    - IQ time series 
    - magnitude phase time series
    - magnitude histogram
    - power spectral density

# TODO

- Subtract away the matched load data in the reductions
- Update the report:
    - show the signal reduction
    - show the matched load reduction
    - show the corrected data (signal - matched load)

## Metadata

- Telescope parameters (reflector parameters):
    - fD
    - name
    - type ?
    - notes

- General:
    - position (lat, long)
    - datetime:
        - start of data collection 
        - end of data collection 
    - load:
        - sky
        - hot
        - cold?
    - notes
    - type:
        - calibration 
        - stare
        - repeat stare
        - frequency switch stare
        - repeat fswitch stare

- SDR (need to keep set & actual process value):
    - center freq
    - gain
    - sample rate
    - n:
        - population of contiguous sample, i.e. 1024 IQ samples 
    - super sample
        - multiple of the sample size, i.e. supersample = 2, then we sample (2 * n) IQ at a time


# hdf5

Use (https://github.com/HDFGroup/hdfview)[hdfview] to inspect the data files.

If you would like to use the cli,

{{{
$ # inspect attributes and groups
$ h5dump -n <path/to/hdf5/file>
$ # inspect attribute value
$ h5dump -a "/path/to/attribute" <path/to/hdf5/file>
$ # inspect dataset (maybe don't do this)
$ h5dump -d "/path/to/dataset" <path/to/hdf5/file>
}}}

- /:
    - latitude 
    - longitude 
    - datetime 
    - row 
    - note 
    - f 
    - D 
    - name 
    - telescope-note 
    - load
    - frequency
    - n
    - super_sample
    - sample_rate
    - data/{n}:
        - frequency 
        - row 
        - super_sample 
        - obs_start_stime 
        - obs_end_stime 
    - data/{n}/IQ:
        - sdr data from antenna
    - data/{n}/reference
        - sdr data from matched load
