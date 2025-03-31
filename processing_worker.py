from PySide6.QtCore import QRunnable, Slot, QObject, Signal
from plot_utils import calculate_grid_values

class WorkerSignals(QObject):
    data = Signal(object)

class ProcessingWorker(QRunnable):
    def __init__(self, path, op, rows_to_skip=3):
        super().__init__()
        self.path = path
        self.op = op
        self.rows_to_skip = rows_to_skip
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        print("CALCULATING GRID VALUES")
        Z = calculate_grid_values(self.path,self.op,self.rows_to_skip)
        print("GRID VALUES CALCULATED")
        self.signals.data.emit(Z)
    