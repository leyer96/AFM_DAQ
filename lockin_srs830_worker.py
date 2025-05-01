from PySide6.QtCore import QRunnable, Slot, QObject, Signal
import numpy as np
from time import sleep

class WorkerSignals(QObject):
    data = Signal(object)
    finished = Signal()
    error = Signal()
    restart = Signal()

class Lockin830Worker(QRunnable):
    def __init__(self,lockin=None,sine_output=0,f0=0,ff=0,f_step=0):
        super().__init__()
        self.signals = WorkerSignals()
        self.lockin = lockin
        self.sine_output = sine_output
        self.f0 = f0
        self.ff = ff
        self.f_step = f_step
        self.fs = np.arange(f0,ff,f_step)
        self.n_steps = int(ff-f0)/f_step
        self.running = True

    @Slot()
    def run(self):
        if self.lockin.id:
            self.lockin.sine_voltage = self.sine_output
            while self.running:
                for f in self.fs:
                    self.lockin.frequency = f
                    sleep((1.5/self.n_steps)*10**-3)
                    # values = self.lockin.snap(val1="R",val2="THeta",val3="PHAse")
                    values = self.lockin.snap(val1="R",val2="THeta")
                    data = {
                        "r": values[0],
                        "theta": values[1],
                        "f": f
                    }
                    self.signals.data.emit(data)
                self.signals.restart.emit()
            self.signals.finished.emit()