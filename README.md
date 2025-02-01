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
