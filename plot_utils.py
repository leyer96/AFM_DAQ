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

def calculate_grid_values(path,op=0,rows_to_skip=0): 
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
    res = line_indexes.size//2
    # PIXEL
    line_indexes = np.reshape(line_indexes, (res,2))
    pixel_data = pixel_data[fs:fe]
    pixel_indexes = np.array([np.linspace(s,s+(e-s)//res*res,res+1) for s,e in line_indexes]) # DATA TRIM
    pixel_indexes = pixel_indexes.astype(int)
    if op == 0:
        # HEIGHT
        height_data = height_data[fs:fe]
        height = np.zeros((res,res))
        for i in range(res):
            for j in range(res):
                ps = pixel_indexes[i,j]
                pe = pixel_indexes[i,j+1]
                height[i,j] = np.mean(height_data[ps:pe])
        Z = remove_linear_trend(height)
    elif op == 1:
        # AMP & PHASE
        amp_data = data["Dev1/ai4"].to_numpy()[fs:fe]
        phase_data = data["Dev1/ai5"].to_numpy()[fs:fe]
        amps = np.zeros((res,res))
        phases = np.zeros((res,res))
        for i in range(res):
            for j in range(res):
                ps = pixel_indexes[i,j]
                pe = pixel_indexes[i,j+1]
                amps[i,j] = np.max(amp_data[ps:pe])
                phases[i,j] = phase_data[np.argmax(amp_data[ps:pe])]
        Z = amps
    return Z

def calculate_grid_values_amp(path, rows_to_skip=0): 
        # ------- CARGAR DATOS -------
        # file_path = os.path.join(desktop_path, ("pe_data.csv"))
        # data = load_data(file_path,rows_to_skip=4)
        # data = data.to_numpy()
        data = np.load(path)
        # -------  FIN -------
        # FRAME
        frame_data = data[:,0]
        frame_indexes = get_signal_indexes_numpy(frame_data)
        fs = frame_indexes[1]
        fe = frame_indexes[2]
        # LINE
        line_data = data[:,1][fs:fe]
        line_indexes = get_signal_indexes_numpy(line_data)[1:-1]
        line_indexes = np.reshape(line_indexes, (line_indexes.size//2,2))
        res = line_indexes.shape[0]
        # PIXEL
        pixel_data = data[:,2][fs:fe]
        pixel_indexes = np.array([np.linspace(s,s+(e-s)//res*res,res+1) for s,e in line_indexes]) # DATA TRIM
        pixel_indexes = pixel_indexes.astype(int)
        # f SWEEP
        sweep_data = data[:,3][fs:fe]
        # AMP & PHASE
        amp_data = data[:,4][fs:fe]
        phase_data = data[:,5][fs:fe]
        amps = np.zeros((res,res))
        phases = np.zeros((res,res))
        for i in range(res):
            for j in range(res):
                ps = pixel_indexes[i,j]
                pe = pixel_indexes[i,j+1]
                amps[i,j] = np.max(amp_data[ps:pe])
                phases[i,j] = phase_data[np.argmax(amp_data[ps:pe])]
        Z = amps
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






