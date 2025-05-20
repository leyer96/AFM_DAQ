import numpy as np
import pandas as pd
from nptdms import TdmsFile

def load_data(path,rows_to_skip=None):
    data = np.array([])
    if path.endswith(".tdms"):
        data = load_tdms(path)
    elif path.endswith(".npy"):
        data = np.load(path)
        data = data.T
    else:
        data = load_csv(path,rows_to_skip=rows_to_skip)
    return data
        
def load_tdms(path):
    try:
        tdms_file = TdmsFile.read(path)
        group = [group.name for group in tdms_file.groups()][0]
        channels = [ch.name for ch in tdms_file[group].channels()]
        data = []
        for channel in channels:
            data.append(tdms_file[group][channel].data)
        data = np.stack(data)
    except Exception as e:
            print(e)
            return None
    return data

def load_csv(path,rows_to_skip=None):
    try:
        if rows_to_skip:
            df = pd.read_csv(path, skiprows=rows_to_skip, dtype=np.float64)
        else:
            df = pd.read_csv(path,dtype=np.float64)
        data = df.to_numpy()
    except Exception as e:
        print(e)
        return None
    else:
        return data.T
    
def attempt_data_load(path):
    for i in range(5):
        if i > 0:
            data = load_data(path, rows_to_skip=i)
        else:
            data = load_data(path)
        if data is not None:
            break
    return data

def get_frame_indexes(frame_data, threshold=2):
    diffs = np.diff(frame_data)
    indexes = np.nonzero(np.abs(diffs) > threshold)[0]
    indexes_diffs = np.diff(indexes)
    max_diff_idx = np.argmax(indexes_diffs)
    fs = indexes[max_diff_idx]
    fe = indexes[max_diff_idx+1]
    return fs,fe
    

def get_line_indexes(data, threshold = 1):
    diffs = np.diff(data)
    indexes = np.nonzero(np.abs(diffs) > threshold)[0]
    rising_edges = indexes[diffs[indexes] > 0] + 1
    rising_edges = remove_close_indexes(rising_edges)
    falling_edges = indexes[diffs[indexes] < 0] + 1
    falling_edges = remove_close_indexes(falling_edges)
    if falling_edges[0] > rising_edges[0]:
        falling_edges = falling_edges[1:]
    min_len = min([rising_edges.size, falling_edges.size])
    rising_edges = rising_edges[0:min_len]
    falling_edges = falling_edges[0:min_len]
    indexes = np.stack([rising_edges,falling_edges])
    n_lines = indexes.shape[1]
    pow2 = np.log2(n_lines)
    if not pow2.is_integer():
        nearest_pow2 = 2**int(np.floor(pow2))
        delta = n_lines - nearest_pow2
        if delta > 1 and delta < 10:
            delta -= 1
            indexes = indexes[:,1:-delta]
        elif delta == 1:
            indexes = indexes[:,1:]
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
    
def remove_close_indexes(indexes, threshold=1000):
    indexes = np.array(indexes)
    diffs = np.diff(indexes)
    to_remove = np.nonzero(diffs < threshold)[0]
    mask = np.ones(len(indexes), dtype=bool)
    mask[to_remove] = False
    return indexes[mask]
    
def calculate_PFM_grid_values(amp_data,phase_data,pixel_indexes,res):
    ext = int(np.min(np.abs(np.gradient(pixel_indexes)[1]))) - 1
    amps = np.zeros((res,res,ext))
    phases = np.zeros((res,res,ext))
    for i in range(res):
        for j in range(res):
            ps = pixel_indexes[i,j]
            pe = pixel_indexes[i,j+1]
            if ps > pe:
                ps_copy = ps
                ps = pe
                pe = ps_copy
            index_max = ps + np.argmax(amp_data[ps:pe])
            x1 = index_max - ext//2
            x2 = index_max + ext//2
            try:
                amps[i,j,:] = amp_data[x1:x2]
                phases[i,j,:] = phase_data[x1:x2] * 18 # CONVERSION FROM V TO DEG.
            except Exception as e:
                print(e)
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






