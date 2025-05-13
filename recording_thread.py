from PySide6.QtCore import QThread, Signal, Slot
from nidaqmx import Task
from nidaqmx.constants import TerminalConfiguration, AcquisitionType, LoggingMode, LoggingOperation
import numpy as np
import time 
AI_CHANNELS = ['Dev1/ai0', 'Dev1/ai1', 'Dev1/ai2', 'Dev1/ai3', 'Dev1/ai4', 'Dev1/ai5', 'Dev1/ai6', 'Dev1/ai7']
class RecordingThread(QThread):
    data = Signal(object)
    recording_started = Signal()
    def __init__(self,n_channels=1,min_v=-10,max_v=10,sample_rate=1000,n_samples=1):
        super().__init__()
        self.task = Task()
        self.n_samples = n_samples
        for i in range(n_channels):
            # self.task.ai_channels.add_ai_voltage_chan(AI_CHANNELS[i], min_val=min_v, max_val=max_v, terminal_config=TerminalConfiguration.RSE)
            self.task.ai_channels.add_ai_voltage_chan(
                AI_CHANNELS[i], 
                min_val=min_v, 
                max_val=max_v, 
                terminal_config=TerminalConfiguration.DIFF)
        self.task.timing.cfg_samp_clk_timing(sample_rate, sample_mode=AcquisitionType.CONTINUOUS)
        self.task.in_stream.configure_logging("./recording.tdms", LoggingMode.LOG_AND_READ, operation=LoggingOperation.CREATE_OR_REPLACE)
        self.is_running = True
        self.n_channels = n_channels
    
    @Slot()
    def run(self):
        self.recording_started.emit()
        try:
            while self.is_running:
                data = self.task.read(number_of_samples_per_channel=self.n_samples)
                self.data.emit(np.array(data))
                time.sleep(0.001)
        except KeyboardInterrupt:
            print("ACQUISITION ABORTED")
        finally:
            self.task.stop()
            self.task.close()
            self.quit()

    def stop(self):
        self.is_running = False