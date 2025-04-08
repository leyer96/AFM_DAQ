from PySide6.QtCore import QThread, Signal, Slot
# from nidaqmx import Task
# from nidaqmx.constants import TerminalConfiguration, AcquisitionType
import numpy as np
AI_CHANNELS = ["Dev1/ai0", "Dev1/ai1", "Dev1/ai2", "Dev1/ai3"]
class AcquisitionThread(QThread):
    data = Signal(list)
    def __init__(self,n_channels=1,min_v=-10,max_v=10,sample_rate=1000,n_samples=1):
        super().__init__()
        self.task = Task()
        for i in range(n_channels):
            self.task.ai_channels.add_ai_voltage_chan(AI_CHANNELS[i], min_val=min_v, max_val=max_v, terminal_config=TerminalConfiguration.RSE)
        self.task.timing.cfg_samp_clk_timing(sample_rate, sample_mode=AcquisitionType.CONTINUOUS)
        self.is_running = True
        self.data_arr = np.array([] for _ in range(n_channels))
        self.n_samples = n_samples
        self.n_channels = n_channels
    
    @Slot()
    def run(self):
        try:
            while True:
                data = self.task.read(number_of_samples_per_channel=self.n_samples)
                self.data.emit(data)
                if not self.is_running:
                    return
        except KeyboardInterrupt:
            print("ACQUISITION ABORTED")

    def stop(self):
        self.is_running = False
