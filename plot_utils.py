import numpy as np
import pandas as pd

def load_data(path,rows_to_skip=None):
    data = np.array([])
    try:
        if rows_to_skip:
            data = pd.read_csv(path, skiprows=rows_to_skip, dtype=np.float64)
        else:
            data = pd.read_csv(path,dtype=np.float64)
    except Exception as e:
        print("EXCEPTION RAISED WHILE LOADING")
        print(e)
        return None
    else:
        print("SUCCESFUL LOADING")
        return data

def get_signal_indexes_numpy(data):
    indexes = np.nonzero(np.absolute(np.diff(data)) > 1)[0]
    indexes[::2] += 1
    return indexes

from scipy.signal import welch, detrend
from scipy.signal.windows import hamming
def get_psd(data):
    try:
        noise = detrend(data) * 47e-9  
        # PSD Parameters
        Fs = 800_000
        nperseg = 4096
        noverlap = nperseg // 2
        ventana = hamming(nperseg)
        frequencies, psd = welch(
            noise, fs=Fs, window=ventana, noverlap=noverlap, nperseg=nperseg
        )
        psd = detrend(psd)
        # Integration range
        a = 12154
        b = 13343
        mask = (frequencies >= a) & (frequencies <= b)
        x_filtered = frequencies[mask]
        y_filtered = psd[mask]
        area = np.trapz(y_filtered, x_filtered)
        Kb = 1.380649e-23
        beta = 0.817
        T = 293
        k = beta * Kb * T / area
        data = {
            "noise": noise,
            "fs": frequencies,
            "psd": psd,
            "k": k
        }
        return data
    except:
        return None

def remove_linear_trend(Z):
    rows,cols = Z.shape
    # REV
    for i in range(rows):
        row = Z[i,:]
        min_val = -np.min(row)
        row -= min_val
        x = np.arange(row.size)
        m1,b1 = np.polyfit(x,row,1)
        Z[i,:] = row - x*m1
    for i in range(cols):
        col = Z[:,i]
        min_val = -np.min(col)
        col -= min_val
        x = np.arange(col.size)
        m2,b2 = np.polyfit(x,col,1)
        Z[:,i] = col - x*m2
    return Z






