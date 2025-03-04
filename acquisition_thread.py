from PySide6.QtCore import QThread, Signal, Slot
from nidaqmx import Task
from nidaqmx.constants import TerminalConfiguration, AcquisitionType
import numpy as np

class AcquisitionThread(QThread):
    data = Signal(list)
    def __init__(self):
        super().__init__()
        self.task = Task()
        self.task.ai_channels.add_ai_voltage_chan("Dev1/ai0", min_val=-10.0, max_val=10.0, terminal_config=TerminalConfiguration.RSE)
        self.task.timing.cfg_samp_clk_timing(1000, sample_mode=AcquisitionType.CONTINUOUS)
        self.is_running = True
        self.data_arr = []
    
    @Slot()
    def run(self):
        try:
            while True:
                data = self.task.read(number_of_samples_per_channel=1)
                self.data_arr = np.concatenate((self.data_arr,data))
                self.data.emit(data)
                if not self.is_running:
                    return
        except KeyboardInterrupt:
            print(data_arr.size)

    def stop(self):
        self.is_running = False
