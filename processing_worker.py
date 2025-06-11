from PySide6.QtCore import QRunnable, Slot, QObject, Signal
from plot_utils import get_line_indexes, attempt_data_load, get_frame_indexes, get_psd, calculate_PFM_grid_values
import numpy as np
from scipy.signal import detrend

class WorkerSignals(QObject):
    data = Signal(object)
    error = Signal(str)
    progress = Signal(int)

class BaseWorker(QRunnable):
    def __init__(self, path, method="MEAN"):
        super().__init__()
        self.path = path
        self.signals = WorkerSignals()
        self.method = method

    def load_data(self):
        data = attempt_data_load(self.path)
        if data is None:
            self.signals.error.emit("ERROR PRESENTED WHILE LOADING DATASET")
            return None
        return data
    
    def get_parsed_sync_data(self, data):
        frame_data = data[0,:]
        line_data = data[1,:]
        # pixel_data = data[:,2]
        # FRAME
        fs,fe = get_frame_indexes(frame_data,threshold=1)
        # LINE
        line_data = line_data[fs:fe]
        line_indexes = get_line_indexes(line_data,threshold=0.25)
        line_indexes = np.fliplr(line_indexes.T)
        for s,e in line_indexes:
            print(f"DISTANCE: {s-e}")
        # RESOLUTION
        res = line_indexes.size//2
        # PIXEL
        pixel_indexes = np.array([
            np.round(np.linspace(np.min([s,e]) + int(np.abs(e-s)*0.075), np.max([s,e]), res + 1)).astype(int)
            for s, e in line_indexes])
        parsed_data = {
            "fs": fs,
            "fe": fe,
            "res": res,
            "pixel_indexes": pixel_indexes
        }
        return parsed_data
    
    def calculate_mean_value_per_line(self,res,pixel_indexes,data,conversion=1):
        Z = np.zeros((res,res))
        for i in range(res):
            for j in range(res):
                ps = pixel_indexes[i,j]
                pe = pixel_indexes[i,j+1]
                try:
                    val = np.mean(data[ps:pe]) * conversion
                    if np.isnan(val):
                        val = np.mean(data[pe:ps]) * conversion
                    Z[i,j] = -val # FIX DAQ INVERSION
                except Exception as e:
                    print(f"PROBLEM ARISED FOR PIXEL {i},{j}: {e}")
        return Z
        
class TopographyWorker(BaseWorker):
    @Slot()
    def run(self):
        self.signals.progress.emit(10) # SIGNAL - PROCESSING STARTED
        try:
            data = self.load_data()
            if data is None:
                return
            self.signals.progress.emit(50) # SIGNAL - DATA LOADED
            parsed_sync_data = self.get_parsed_sync_data(data)
            fs = parsed_sync_data["fs"]
            fe = parsed_sync_data["fe"]
            res = parsed_sync_data["res"]
            pixel_indexes = parsed_sync_data["pixel_indexes"]
            self.signals.progress.emit(75)
            # HEIGHT
            height_data = data[3,][fs:fe]
            # CALCULATE HEIGHT PER PIXEL
            Z = self.calculate_mean_value_per_line(res,pixel_indexes,height_data)
            self.signals.data.emit(Z)
            self.signals.progress.emit(100)
        except Exception as e:
            print(e)
            self.signals.error.emit(e)

class PSDWorker(BaseWorker):
    @Slot()
    def run(self):
        self.signals.progress.emit(10)
        try:
            data = self.load_data()
            if data is None:
                return
            self.signals.progress.emit(50)
            noise = data[0,:]
            psd_data = get_psd(noise)
            self.signals.data.emit(psd_data)
            self.signals.progress.emit(100)
        except Exception as e:
            print(e)
            self.signals.error.emit(f"ERROR WHILE PROCESSING: {e}")

class PFMWorker(BaseWorker):
    @Slot()
    def run(self):
        try:
            data = self.load_data()
            if data is None:
                return
            self.signals.progress.emit(50)
            parsed_sync_data = self.get_parsed_sync_data(data)
            fs = parsed_sync_data["fs"]
            fe = parsed_sync_data["fe"]
            res = parsed_sync_data["res"]
            pixel_indexes = parsed_sync_data["pixel_indexes"]
            self.signals.progress.emit(75)
            # AMP DATA
            amp_data = data[4,:][fs:fe]
            amp = self.calculate_mean_value_per_line(res,pixel_indexes,amp_data)
            # PHASE DATA
            phase_data = data[5,:][fs:fe]
            phase = self.calculate_mean_value_per_line(res,pixel_indexes,phase_data)
            amp_and_phase = np.stack([amp,phase])
            self.signals.data.emit(amp_and_phase)
            self.signals.progress.emit(100)
        except Exception as e:
            print(e)
            self.signals.error.emit(f"ERROR WHILE PROCESSING: {e}")

class LVPFMWorker(BaseWorker):
    @Slot()
    def run(self):
        try:
            data = self.load_data()
            if data is None:
                return
            self.signals.progress.emit(50)
            parsed_sync_data = self.get_parsed_sync_data(data)
            fs = parsed_sync_data["fs"]
            fe = parsed_sync_data["fe"]
            res = parsed_sync_data["res"]
            pixel_indexes = parsed_sync_data["pixel_indexes"]
            self.signals.progress.emit(75)
            # AMP DATA
            amp_data = data[4,:][fs:fe]
            amp2_data = data[6,:][fs:fe]
            # PHASE DATA
            phase_data = data[5,:][fs:fe]
            phase2_data = data[7,:][fs:fe]
            if self.method == "MEAN":
                amp = self.calculate_mean_value_per_line(res,pixel_indexes,amp_data)
                amp2 = self.calculate_mean_value_per_line(res,pixel_indexes,amp2_data)
                phase = self.calculate_mean_value_per_line(res,pixel_indexes,phase_data,conversion=18)
                phase2 = self.calculate_mean_value_per_line(res,pixel_indexes,phase2_data,conversion=18)
                amps_and_phases = np.stack([
                    amp,
                    amp2,
                    phase,
                    phase2
                ])
            else:
                amp_and_phase = calculate_PFM_grid_values(amp_data,phase_data,pixel_indexes,res)
                amp_and_phase2 = calculate_PFM_grid_values(amp2_data,phase2_data,pixel_indexes,res)
                amps_and_phases = np.stack([
                    amp_and_phase[0,:],
                    amp_and_phase[1,:],
                    amp_and_phase2[0,:],
                    amp_and_phase2[1,:]
                    ])
            self.signals.progress.emit(95)
            self.signals.data.emit(amps_and_phases)
            self.signals.progress.emit(100)
        except Exception as e:
            print(e)
            self.signals.error.emit(f"ERROR WHILE PROCESSING: {e}")

    