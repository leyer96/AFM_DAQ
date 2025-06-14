from PySide6.QtCore import QThread, Signal, Slot
from nidaqmx import Task
from nidaqmx.constants import TerminalConfiguration, AcquisitionType
import numpy as np
import time 
AI_CHANNELS = ['Dev1/ai0', 'Dev1/ai1', 'Dev1/ai2', 'Dev1/ai3', 'Dev1/ai4', 'Dev1/ai5', 'Dev1/ai6', 'Dev1/ai7']
class AcquisitionThread(QThread):
    data = Signal(object)
    def __init__(self,n_channels=1,min_v=-10,max_v=10,sample_rate=1000,n_samples=1, terminal_config="DIFF"):
        super().__init__()
        self.config = {
            "n_channels": n_channels,
            "min_v": min_v,
            "max_v": max_v,
            "sample_rate": sample_rate,
            "n_samples": n_samples,
            "terminal_config": None
        }
        self.config["terminal_config"] = TerminalConfiguration.DIFF if terminal_config == "DIFF" else TerminalConfiguration.RSE
        self.task = Task()
        self.is_running = True
    
    @Slot()
    def run(self):
        self.task = Task()
        for i in range(self.config["n_channels"]):
            # self.task.ai_channels.add_ai_voltage_chan(AI_CHANNELS[i], min_val=min_v, max_val=max_v, terminal_config=TerminalConfiguration.RSE)
            self.task.ai_channels.add_ai_voltage_chan(
                AI_CHANNELS[i], 
                min_val=self.config["min_v"], 
                max_val=self.config["max_v"], 
                terminal_config=self.config["terminal_config"])
        self.task.timing.cfg_samp_clk_timing(self.config["sample_rate"], sample_mode=AcquisitionType.CONTINUOUS)
        try:
            while self.is_running:
                data = self.task.read(number_of_samples_per_channel=self.config["n_samples"])
                self.data.emit(np.array(data), copy=True)
                time.sleep(0.001)
        except KeyboardInterrupt:
            print("ACQUISITION ABORTED")
        finally:
            self.task.stop()
            self.task.close()
            self.quit()

    def stop(self):
        self.is_running = False