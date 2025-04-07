from PySide6.QtCore import QRunnable, Slot, QObject, Signal
import numpy as np
from time import sleep

class WorkerSignals(QObject):
    data = Signal(object)

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

    @Slot()
    def run(self):
        if self.lockin.id:
            self.lockin.sine_voltage = self.sine_output
            for f in self.fs:
                self.lockin.frequency = f
                sleep(0.1)
                values = self.lockin.snap(val1="R",val2="THeta",val3="PHAse")
                data = {
                    "r": values[0],
                    "theta": values[1],
                    "f": f
                }
                self.signals.data.emit(data)