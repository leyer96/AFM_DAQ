from PySide6.QtCore import QRunnable, Slot, QObject, Signal
from plot_utils import get_signal_indexes_numpy, load_data, remove_linear_trend
import numpy as np

class WorkerSignals(QObject):
    data = Signal(object)
    error = Signal(str)
    progress = Signal(int)

class ProcessingWorker(QRunnable):
    def __init__(self, path, op, rows_to_skip=3):
        super().__init__()
        self.path = path
        self.op = op
        self.rows_to_skip = rows_to_skip
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        path = self.path
        op = self.op
        rows_to_skip = self.rows_to_skip
        try:
            if path.endswith(".csv"):
                try:
                    self.signals.progress.emit(10)
                    data = load_data(path,rows_to_skip)
                except:
                    self.signals.error.emit("ERROR PRESENTED WHILE LOADING DATASET")
                else:
                    self.signals.progress.emit(50)
                frame_data = data["Dev1/ai0"].to_numpy()
                line_data = data["Dev1/ai1"].to_numpy()
                pixel_data = data["Dev1/ai2"].to_numpy()
                height_data = data["Dev1/ai3"].to_numpy()
                if op == 1:
                    amp_data = data["Dev1/ai4"].to_numpy()[fs:fe]
                    phase_data = data["Dev1/ai5"].to_numpy()[fs:fe]
            elif path.endswith(".npy"):
                self.signals.progress.emit(25)
                data = np.load(path)
                frame_data = data[:,0]
                line_data = data[:,1]
                pixel_data = data[:,2]
                height_data = data[:,3]
                if op == 1:
                    amp_data = data[:,4]
                    phase_data = data[:,5]

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
            try:
                line_indexes = np.reshape(line_indexes, (res,2))
            except:
                line_indexes = np.reshape(line_indexes[1:], (res,2))
            pixel_data = pixel_data[fs:fe]
            pixel_indexes = np.array([np.linspace(s,s+(e-s)//res*res,res+1) for s,e in line_indexes]) # DATA TRIM
            pixel_indexes = pixel_indexes.astype(int)
            self.signals.progress.emit(75)
            if op == 0:
                # HEIGHT
                height_data = height_data[fs:fe]
                height = np.zeros((res,res))
                for i in range(res):
                    for j in range(res):
                        ps = pixel_indexes[i,j]
                        pe = pixel_indexes[i,j+1]
                        height[i,j] = np.mean(height_data[ps:pe])
                print(f"HEIGHT MIN: {np.min(np.abs(height))}")
                Z = height * -1090.91 
                Z += np.max(np.abs(Z))
                # Z = (height - np.max(np.abs(height))) * -1090.91 
                # Z = height 
                # Z = remove_linear_trend(height)
            elif op == 1:
                # AMP & PHASE
                amp_data = amp_data[fs:fe]
                phase_data = phase_data[fs:fe]
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
                Z = np.stack((amps, phases))
            self.signals.data.emit(Z)
            self.signals.progress.emit(100)
        except:
            self.signals.error.emit("ERROR WHILE PROCESSING")
    