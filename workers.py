from PySide6.QtCore import QRunnable, Slot, QObject, Signal
from nptdms import TdmsFile
import numpy as np
import os


class WorkerSignals(QObject):
    finished = Signal()
    error = Signal()

class ConverterWorker(QRunnable):
    def __init__(self, path, target,mode="csv"):
        super().__init__()
        self.signals = WorkerSignals()
        self.path = path
        self.mode = mode
        fn = os.path.basename(path)
        self.fn = os.path.splitext(fn)[0]
        self.target = os.path.join(target,self.fn+"-copy")



    @Slot()
    def run(self):
        try:
            tdms_file = TdmsFile.read(self.path)
            df = tdms_file.as_dataframe()
            if self.mode == "csv":
                df.to_csv(self.target+".csv", index=False)
            else:
                np.save(self.target, df.to_numpy())
            self.signals.finished.emit()
        except Exception as e:
            print(e)
            self.signals.error.emit()
        