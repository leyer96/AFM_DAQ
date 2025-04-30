import numpy as np
import pandas as pd

def load_data(path, rows_to_skip=0):
    data = np.array([])
    try:
        # data = pd.read_csv(path, skiprows=rows_to_skip)
        data = pd.read_csv(path)
    except Exception as e:
        print(e)
    return data

def get_signal_indexes_numpy(data):
    indexes = np.nonzero(np.absolute(np.diff(data)) > 1)[0]
    indexes[::2] += 1
    return indexes


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






