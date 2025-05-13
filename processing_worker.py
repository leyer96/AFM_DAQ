from PySide6.QtCore import QRunnable, Slot, QObject, Signal
from plot_utils import get_signal_indexes_numpy, attempt_data_load, remove_linear_trend, get_psd, calculate_PFM_grid_values
import numpy as np

class WorkerSignals(QObject):
    data = Signal(object)
    error = Signal(str)
    progress = Signal(int)

class ProcessingWorker(QRunnable):
    def __init__(self, path, op):
        super().__init__()
        self.path = path
        self.op = op
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        path = self.path
        op = self.op
        self.signals.progress.emit(10)
        try:
            data = attempt_data_load(path)
            if data is None:
                self.signals.error.emit("ERROR PRESENTED WHILE LOADING DATASET")
                return
            self.signals.progress.emit(50)
            if op == "PSD": # PSD processing
                noise = data[0,:]
                # noise = data["Dev1/ai0"].to_numpy()
                psd_data = get_psd(noise)
                self.signals.data.emit(psd_data)
                self.signals.progress.emit(100)
                return 
            # frame_data = data["Dev1/ai0"].to_numpy()
            frame_data = data[0,:]
            # line_data = data["Dev1/ai1"].to_numpy()
            line_data = data[1,:]
            # pixel_data = data["Dev1/ai2"].to_numpy()
            height_data = data[2,:]
            # height_data = data["Dev1/ai3"].to_numpy()
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
            if line_indexes.size % 2 == 0:
                line_indexes = np.reshape(line_indexes, (res,2))
            else:
                line_indexes = np.reshape(line_indexes[1:], (res,2))
            # pixel_data = pixel_data[fs:fe]
            pixel_indexes = np.array([np.linspace(s,s+(e-s)//res*res,res+1) for s,e in line_indexes]) # DATA TRIM
            pixel_indexes = pixel_indexes.astype(int)
            self.signals.progress.emit(75)
            if op == "Topography":
                # HEIGHT
                height_data = height_data[fs:fe]
                height = np.zeros((res,res))
                for i in range(res):
                    for j in range(res):
                        ps = pixel_indexes[i,j]
                        pe = pixel_indexes[i,j+1]
                        height[i,j] = np.mean(height_data[ps:pe])
                Z = -height
            elif op == "PFM" or op == "PFM - MultiFreq":
                # AMP & PHASE
                # amp_data = data["Dev1/ai4"].to_numpy()[fs:fe]
                amp_data = data[4,:][fs:fe]
                # phase_data = data["Dev1/ai5"].to_numpy()[fs:fe]
                phase_data = data[5,:][fs:fe]
                Z = calculate_PFM_grid_values(amp_data,phase_data,pixel_indexes,res)
                if op == "PFM - MultiFreq":
                    # amp_lateral_data = data["Dev1/ai6"].to_numpy()[fs:fe]
                    amp_lateral_data = data[5,:][fs:fe]
                    # phase_lateral_data = data["Dev1/ai7"].to_numpy()[fs:fe]
                    phase_lateral_data = data[6,:][fs:fe]
                    Z2 = calculate_PFM_grid_values(amp_lateral_data,phase_lateral_data,pixel_indexes,res)
                    Z = np.stack(Z,Z2)
            self.signals.data.emit(Z)
            self.signals.progress.emit(100)
        except Exception as e:
            print(e)
            self.signals.error.emit(f"ERROR WHILE PROCESSING: {e}")

    