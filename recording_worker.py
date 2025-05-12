from PySide6.QtCore import QRunnable, Slot, QObject, Signal, QThread
import pandas as pd

class WorkerSignals(QObject):
    error = Signal(str)

class RecordingWorker(QRunnable):
    def __init__(self, filepath=None, csv_columns=None, new_data=None):
        super().__init__()
        self.filepath = filepath
        self.csv_columns = csv_columns
        self.new_data = new_data
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            df = pd.DataFrame(self.new_data.T, columns=self.csv_columns)
            df.to_csv(self.filepath, mode='a', header=False, index=False)
        except:
            self.signals.error.emit()

import csv
class RecordingThread(QThread):
    def __init__(self, filepath=None, csv_columns=None, new_data=None):
        self.filepath = filepath
        self.csv_columns = csv_columns
        self.new_data = new_data
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            df = pd.DataFrame(self.new_data.T, columns=self.csv_columns)
            df.to_csv(self.filepath, mode='a', header=False, index=False)
        except:
            self.signals.error.emit()

