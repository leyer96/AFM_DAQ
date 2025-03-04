import numpy as np
import pandas as pd

def load_data(path, rows_to_skip=0):
    data = np.array([])
    try:
        data = pd.read_csv(path, skiprows=rows_to_skip)
    except Exception as e:
        print(e)
    return data

def get_signal_indexes_numpy(data):
    indexes = np.nonzero(np.absolute(np.diff(data)) > 1)[0]
    indexes[::2] += 1
    return indexes

def calculate_grid_values(path,rows_to_skip=0): 
    # LOAD
    data = load_data(path,rows_to_skip)
    frame_data = data["Dev1/ai0"].to_numpy()
    line_data = data["Dev1/ai1"].to_numpy()
    pixel_data = data["Dev1/ai2"].to_numpy()
    height_data = data["Dev1/ai3"].to_numpy()
    # FRAME
    frame_indexes = get_signal_indexes_numpy(frame_data)
    fs = frame_indexes[1]
    fe = frame_indexes[2]
    # LINE
    line_data = line_data[fs:fe]
    line_indexes = get_signal_indexes_numpy(line_data)
    # RESOLUTION
    res = int(line_indexes.size/2) - 1
    # PIXEL
    line_indexes_stack = np.reshape(line_indexes,(res+1,2))
    pixel_data = pixel_data[fs:fe]
    pixel_indexes = get_signal_indexes_numpy(pixel_data)
    pixel_indexes_stack = np.array(
        [
            [pixel_indexes[pixel_indexes >= start][0],pixel_indexes[pixel_indexes <= end][-1]] for start,end in line_indexes_stack
            ])
    pixel_indexes_stack = pixel_indexes_stack[1:]
    # HEIGHT
    height_data = height_data[fs:fe]
    Z = np.mean(np.array([np.hsplit(height_data[index_stack[0]:index_stack[0]+int(17000/res)*res],res) for index_stack in pixel_indexes_stack]),axis=2)
    Z = remove_linear_trend(Z)
    return Z

def remove_linear_trend(Z):
    for i in range(len(Z)):
        xi = Z[i,:]
        yi = Z[:,i]
        x = np.arange(xi.size)
        m1,b1 = np.polyfit(x,xi,1)
        m2,b2 = np.polyfit(x,yi,1)
        Z[i,:] -= x*m1
        Z[:,i] -= x*m2
    return Z






