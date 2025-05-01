from PySide6.QtCore import QRunnable, Slot, QObject, Signal
import numpy as np
from time import sleep

class WorkerSignals(QObject):
    data = Signal(object)
    finished = Signal()
    restart = Signal()
    failed_connection = Signal()

class LockinWorker(QRunnable):
    def __init__(self,lockin=None,sine_output=0,f0=0,ff=0,f_step=0):
        super().__init__()
        self.signals = WorkerSignals()
        self.lockin = lockin
        self.sine_output = sine_output
        self.f0 = f0
        self.ff = ff
        self.f_step = f_step
        self.fs = np.arange(f0,ff,f_step)
        self.running = True
        self.n_steps = int((ff-f0)/f_step)

    @Slot()
    def run(self):
        if self.lockin.check_id():
            self.lockin.ref.sine_out_amplitude = self.sine_output
            while self.running:
                for f in self.fs:
                    self.lockin.ref.frequency = f
                    sleep((1.5/self.n_steps)*10**-3)
                    r = self.lockin.data.value[2]
                    theta = self.lockin.data.value["Theta"]
                    data = {
                        "r": r,
                        "theta": theta,
                        "f": f
                    }
                    self.signals.data.emit(data)
                self.signals.restart.emit()
            self.signals.finished.emit()
        else:
            self.signals.failed_connection.emit()