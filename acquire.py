from threading import Thread
from PySide6.QtWidgets import(
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget
)
from PySide6.QtCore import QThreadPool, QTimer
from PySide6.QtGui import QIcon
# from acquisition_thread import AcquisitionThread
from utils import Paths
import pyqtgraph as pg
import numpy as np
import csv
## TEST
import random
import time

class AcquireTab(QWidget):
    def __init__(self):
        super().__init__()
        # WIDGETS
        self.n_channels_input = QSpinBox() 
        self.channel_selection_input = QComboBox()
        self.min_input_value_input = QDoubleSpinBox()
        self.max_input_value_input = QDoubleSpinBox()
        self.sample_rate_input = QDoubleSpinBox()
        self.n_samples_input = QSpinBox()
        self.n_cicles_input = QSpinBox()
        self.n_cicles = QLabel()
        self.filename_input = QLineEdit(text="datos_daq.csv")
        self.plot_widget = pg.PlotWidget()
        record_btn = QPushButton("RECORD")
        stop_btn = QPushButton("STOP")
        
        # DATA
        self.channels_data = np.zeros(1)
        self.plots = np.zeros(1)

        # CONFIG
        # THREADS
        self.threadpool = QThreadPool()
        ## PLOT
        self.plot_widget.setXRange(1,100)
        ## INPUTS
        self.n_channels_input.setRange(-10,10)
        self.n_channels_input.setValue(1)
        self.channel_selection_input.addItems(["All","Dev1/ai0", "Dev1/ai1", "Dev1/ai2", "Dev1/ai3", "Dev1/ai4", "Dev1/ai5"])
        self.sample_rate_input.setValue(1000)
        self.sample_rate_input.setRange(0,100*1000)
        self.min_input_value_input.setRange(-10,10)
        self.min_input_value_input.setValue(-10)
        self.max_input_value_input.setRange(-10,10)
        self.max_input_value_input.setValue(10)
        self.n_samples_input.setRange(0,999999)
        self.n_samples_input.setValue(1000)
        ## ICONS
        record_btn.setIcon(QIcon(Paths.icon("control-record.png")))
        stop_btn.setIcon(QIcon(Paths.icon("control-stop-square.png")))

        # SIGNALS
        self.n_channels_input.valueChanged.connect(self.set_n_of_channels)
        self.min_input_value_input.valueChanged.connect(self.set_max_input)

        #LAYOUT
        form = QFormLayout()
        form.addRow("Number of channels to acquire", self.n_channels_input)
        form.addRow("Plot channel", self.channel_selection_input)
        form.addRow("Min. Value", self.min_input_value_input)
        form.addRow("Max. Value", self.max_input_value_input)
        form.addRow("DAQ Sample Rate", self.sample_rate_input)
        form.addRow("Number of Samples", self.n_samples_input)
        form.addRow("Number of Cicles", self.n_cicles_input)
        form.addRow("Filename", self.filename_input)
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        layout.addLayout(form)
        layout.addWidget(record_btn)
        layout.addWidget(stop_btn)

        self.setLayout(layout)
        
        ##TEST
        self.plot_widget.setYRange(-1,1)
        # self.acquisition_thread = AcquisitionThread()
        # self.acquisition_thread.data.connect(self.on_new_data)
        self.curve = self.plot_widget.plot(self.channels_data, pen='y')
        record_btn.clicked.connect(self.start_acquisition)
        stop_btn.clicked.connect(self.stop_acquisition)
        self.prev_data = np.array([])
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(1000)
    
    def set_n_of_channels(self,n):
        arr = [[] for _ in range(n)]
        self.channels_data = np.array(arr)
        self.prev_data = np.array(arr)
        self.plots = np.zeros((self.channels_data.shape[1],1000)) # CAMBIAR 1000

    def set_max_input(self,min):
        self.max_input_value_input.setMinimum(min)
    
    def start_acquisition(self):
        min_v = self.min_input_value_input.value()
        max_v = self.max_input_value_input.value()
        sample_rate = self.sample_rate_input.value()
        n_samples = self.n_samples_input.value()
        self.acquisition_thread.start(min_v=min_v,max_v=max_v,sample_rate=sample_rate,n_samples=n_samples)

    def stop_acquisition(self):
        if self.acquisition_thread.is_running:
            self.acquisition_thread.stop()

    def update_plot(self):
        new_data = self.channels_data
        delta = new_data.shape[1] - self.prev_data.shape[1]
        self.plots = np.roll(self.plots, -delta)
        self.plots[::,-delta] = new_data[::,-delta]
        self.prev_data = self.channels_data
        self.curve.setData(self.plots)

    def on_new_data(self, data):
        self.channels_data = np.concatenate((self.channel_data,data),axis=1)


    # def acquire_and_save_data(self):
    #     with open(self.file_path, 'w', newline='') as csvfile:
    #         csv_writer = csv.writer(csvfile)
    #         headers = [f"Channel_{i+1}" for i in range(self.num_channels_var.value())]
    #         csv_writer.writerow(headers)

    #     while self.is_running:
    #         data = self.task.read(number_of_samples_per_channel=1)
    #         with open(self.file_path, 'a', newline='') as csvfile:
    #             csv_writer = csv.writer(csvfile)
    #             csv_writer.writerow([float(e[0]) for e in data])
    #             self.update_plot(data)

    # def update_plot(self, new_data):
    #     for i, d in enumerate(new_data):
    #         if i < self.num_channels_var.value():
    #             self.channel_data[i].append(float(d[0]))
    #             if len(self.channel_data[i]) > len(self.channel_data[0]):
    #                 self.channel_data[i].pop(0)  # Remove oldest data point
    #             if len(self.lines) < self.num_channels_var.value():
    #                 line, = self.ax.plot([], [], color=self.colors[i], label=f'Channel {i+1}')
    #                 self.lines.append(line)
    #             self.lines[i].set_data(range(len(self.channel_data[0])), self.channel_data[i])
    #     self.ax.relim()
    #     self.ax.autoscale_view()
    #     self.ax.legend()
    #     self.canvas.draw()

    # def start_acquisition(self):
    #     self.file_path = self.filename_var.text()
    #     self.configure_daq()
    #     self.is_running = True
    #     self.acquisition_thread = Thread(target=self.acquire_and_save_data)
    #     self.acquisition_thread.start()

    # def stop_acquisition(self):
    #     self.is_running = False
    #     self.acquisition_thread.join()
    #     self.task.stop()
    #     self.task.close()
    #     print("Acquisition stopped.")