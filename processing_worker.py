from PySide6.QtCore import QRunnable, Slot, QObject, Signal
from plot_utils import get_line_indexes, attempt_data_load, get_frame_indexes, get_psd, calculate_PFM_grid_values
import numpy as np
from scipy.signal import detrend

class WorkerSignals(QObject):
    data = Signal(object)
    error = Signal(str)
    progress = Signal(int)

class BaseWorker(QRunnable):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.signals = WorkerSignals()

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
        line_indexes = get_line_indexes(line_data,threshold=0.5)
        line_indexes = np.fliplr(line_indexes.T)
        # RESOLUTION
        res = line_indexes.size//2
        # PIXEL
        pixel_indexes = np.array([
            np.round(np.linspace(s, e, res + 1)).astype(int)
            for s, e in line_indexes])
        parsed_data = {
            "fs": fs,
            "fe": fe,
            "res": res,
            "pixel_indexes": pixel_indexes
        }
        return parsed_data
        
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
            height = np.zeros((res,res))
            # CALCULATE HEIGHT PER PIXEL
            for i in range(res):
                for j in range(res):
                    ps = pixel_indexes[i,j]
                    pe = pixel_indexes[i,j+1]
                    try:
                        h = np.mean(height_data[ps:pe])
                        if np.isnan(h):
                            h = np.mean(height_data[pe:ps])
                        height[i,j] = h
                    except Exception as e:
                        print(f"PROBLEM ARISED FOR PIXEL {i},{j}: {e}")
                Z = -height
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
            # PHASE DATA
            phase_data = data[5,:][fs:fe]
            amp_and_phase = calculate_PFM_grid_values(amp_data,phase_data,pixel_indexes,res)
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
            phase2_data = data[5,:][fs:fe]
            amp_and_phase = calculate_PFM_grid_values(amp_data,phase_data,pixel_indexes,res)
            self.signals.progress.emit(85)
            amp_and_phase2 = calculate_PFM_grid_values(amp2_data,phase2_data,pixel_indexes,res)
            self.signals.progress.emit(95)
            amps_and_phases = np.stack([
                amp_and_phase[0,:],
                amp_and_phase[1,:],
                amp_and_phase2[0,:],
                amp_and_phase2[1,:]
                ])
            self.signals.data.emit(amps_and_phases)
            self.signals.progress.emit(100)
        except Exception as e:
            print(e)
            self.signals.error.emit(f"ERROR WHILE PROCESSING: {e}")

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
                psd_data = get_psd(noise)
                self.signals.data.emit(psd_data)
                self.signals.progress.emit(100)
                return 
            print(f"DATA SHAPE IS {data.shape}")
            frame_data = data[0,:]
            line_data = data[1,:]
            # pixel_data = data[:,2]
            height_data = data[3,:]
            # FRAME
            fs,fe = get_frame_indexes(frame_data,threshold=2)
            print(f"FS: {fs} & FE: {fe}")
            # LINE
            line_data = line_data[fs:fe]
            line_indexes = get_line_indexes(line_data,threshold=1.8)
            line_indexes = np.fliplr(line_indexes.T)
            # RESOLUTION
            res = line_indexes.size//2
            print(f"RES: {res}")
            print(f"LINE INDEXES SHAPE {line_indexes.shape}")
            # PIXEL
            pixel_indexes = np.array([np.linspace(s,s+(e-s)//res*res,res+1) for s,e in line_indexes]) # DATA TRIM
            print(f"PIXEL INDEXES SHAPE {pixel_indexes.shape}")
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
                        try:
                            h = np.mean(height_data[ps:pe])
                            if np.isnan(h):
                                h = np.mean(height_data[pe:ps])
                            height[i,j] = h
                        except Exception as e:
                            print(f"PROBLEM ARISED FOR PIXEL {i},{j}: {e}")
                # Z = detrend(-height)
                Z = -height
            elif op == "PFM" or op == "PFM - MultiFreq":
                # AMP & PHASE
                amp_data = data[4,:][fs:fe]
                phase_data = data[5,:][fs:fe]
                Z = calculate_PFM_grid_values(amp_data,phase_data,pixel_indexes,res)
                if op == "PFM - MultiFreq":
                    print(f"CALCULATING MULTI FREQ")
                    amp_lateral_data = data[6,:][fs:fe]
                    phase_lateral_data = data[7,:][fs:fe]
                    Z2 = calculate_PFM_grid_values(amp_lateral_data,phase_lateral_data,pixel_indexes,res)
                    Z = np.stack([Z[0,:],Z[1,:],Z2[0,:],Z2[1,:]])
                    print(f"DATA EMITED")
            self.signals.data.emit(Z)
            self.signals.progress.emit(100)
        except Exception as e:
            print(e)
            self.signals.error.emit(f"ERROR WHILE PROCESSING: {e}")

    