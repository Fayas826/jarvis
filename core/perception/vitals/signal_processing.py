import scipy.signal as signal
import numpy as np

def butter_bandpass_filter(data, lowcut=0.75, highcut=3.33, fs=30.0, order=2):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    if len(data) > 15:
        return signal.filtfilt(b, a, data)
    return data

def calculate_psd(data, fs=30.0):
    if len(data) < 30:
        return [], []
    f, p = signal.welch(data, fs, nperseg=min(len(data), 256))
    return f, p
