from PySide6.QtCore import QThread, Signal, Slot
from nidaqmx import Task
from nidaqmx.constants import TerminalConfiguration, AcquisitionType
import numpy as np

class AcquisitionThread(QThread):
    data = Signal(list)
    def __init__(self,min_v=-10,max_v=10,sample_rate=1000,n_samples=1):
        super().__init__()
        self.task = Task()
        self.task.ai_channels.add_ai_voltage_chan("Dev1/ai0", min_val=min_v, max_val=max_v, terminal_config=TerminalConfiguration.RSE)
        self.task.timing.cfg_samp_clk_timing(sample_rate, sample_mode=AcquisitionType.CONTINUOUS)
        self.is_running = True
        self.data_arr = []
        self.n_samples = n_samples
    
    @Slot()
    def run(self):
        try:
            while True:
                data = self.task.read(number_of_samples_per_channel=self.n_samples)
                self.data_arr = np.concatenate((self.data_arr,data))
                self.data.emit(data)
                if not self.is_running:
                    return
        except KeyboardInterrupt:
            print("ACQUISITION ABORTED")

    def stop(self):
        self.is_running = False
