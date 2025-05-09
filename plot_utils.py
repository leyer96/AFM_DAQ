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
    
def attempt_data_load(path):
    for i in range(5):
        if i > 0:
            data = load_data(path, rows_to_skip=i)
        else:
            data = load_data(path)
        if data is not None:
            break
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
    
def calculate_PFM_grid_values(amp_data,phase_data,pixel_indexes,res):
    ext = 300
    amps = np.zeros((res,res,ext))
    phases = np.zeros((res,res,ext))
    for i in range(res):
        for j in range(res):
            ps = pixel_indexes[i,j]
            pe = pixel_indexes[i,j+1]
            index_max = int(ps + ext//2 + np.argmax(amp_data[ps+ext//2:pe-ext//2]))
            x1 = int(index_max - ext//2)             
            x2 = int(index_max + ext//2)
            if x1 > ps and x2 < pe:
                amps[i,j,:] = amp_data[x1:x2]
                phases[i,j,:] = phase_data[x1:x2]
            else:
                amps[i,j,:] = 0
                phases[i,j,:] = 0
            amps[i,j,0] = np.max(amp_data[ps:pe])
            phases[i,j,0] = phase_data[index_max]
    stack = np.stack((amps, phases))
    return stack

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






