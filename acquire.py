from threading import Thread
from PySide6.QtWidgets import(
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
# from acquisition_thread import AcquisitionThread
from widgets import ConnectionStatusIndicator
from utils import Paths
import pyqtgraph as pg
import numpy as np


class AcquireTab(QWidget):
    def __init__(self):
        super().__init__()
        # ---- WIDGETS ---- #
        ## PLOT WIDGET
        self.plot_widget = pg.PlotWidget()
        self.stream_data_option = QCheckBox("Stream data")
        ## DAQ CONFIG INPUT WIDGETS
        self.n_channels_input = QSpinBox() 
        self.channel_selection_input = QComboBox()
        self.min_input_value_input = QDoubleSpinBox()
        self.max_input_value_input = QDoubleSpinBox()
        self.sample_rate_input = QDoubleSpinBox()
        self.n_samples_input = QSpinBox()
        self.n_cicles_input = QSpinBox()
        self.n_cicles = QLabel()
        ## RECORDING CONTROLS
        self.filename_input = QLineEdit(text="datos_daq.csv")
        record_btn = QPushButton("RECORD")
        stop_btn = QPushButton("STOP")
        
        # ---- DATA ---- #
        self.channels_data = np.array([])
        self.plots = np.zeros(100) # CAMBIAR

        # ---- CONFIG ---- #
        self.DAQ_connected = False
        ## THREADS
        ## PLOT
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

        # ---- SIGNALS ---- #
        self.n_channels_input.valueChanged.connect(self.set_n_of_channels)
        self.min_input_value_input.valueChanged.connect(self.set_max_input)

        # ---- LAYOUT ---- #
        ## FORM - DAQ CONFIG
        form = QFormLayout()
        form.addRow("Number of channels to acquire", self.n_channels_input)
        form.addRow("Plot channel", self.channel_selection_input)
        form.addRow("Min. Value", self.min_input_value_input)
        form.addRow("Max. Value", self.max_input_value_input)
        form.addRow("DAQ Sample Rate", self.sample_rate_input)
        form.addRow("Number of Samples", self.n_samples_input)
        form.addRow("Number of Cicles", self.n_cicles_input)
        form.addRow("Filename", self.filename_input)
        ## MAIN LAYOUT
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        layout.addWidget(self.stream_data_option)
        layout.addLayout(form)
        layout.addWidget(record_btn)
        layout.addWidget(stop_btn)

        self.setLayout(layout)
        
        # ---- TEST ---- #
        self.plot_widget.setXRange(1,100)
        self.plot_widget.setYRange(-0.4,0.4)
        self.curve = self.plot_widget.plot(self.channels_data, pen='y')
        record_btn.clicked.connect(self.start_acquisition)
        stop_btn.clicked.connect(self.stop_acquisition)
        self.prev_data = np.array([])
        self.is_running = False
        self.plot_timer = QTimer(self)
        self.plot_timer.timeout.connect(self.update_plot)
        self.plot_timer.start(100)
        self.connection_timer = QTimer(self)
        self.connection_timer.timeout.connect(self.check_connection_status)
        self.connection_timer.start(3000)
        # ----- TEST -----

    
    def set_n_of_channels(self,n):
        arr = [[] for _ in range(n)]
        self.channels_data = np.array(arr)
        self.prev_data = np.array(arr)
        self.plots = np.zeros((self.channels_data.shape[1],100)) # CAMBIAR

    def set_max_input(self,min):
        self.max_input_value_input.setMinimum(min)
    
    def start_acquisition(self):
        n_channels = self.n_channels_input.value()
        min_v = self.min_input_value_input.value()
        max_v = self.max_input_value_input.value()
        sample_rate = self.sample_rate_input.value()
        n_samples = self.n_samples_input.value()
        # self.acquisition_thread = AcquisitionThread(n_channels=n_channels,min_v=min_v,max_v=max_v,sample_rate=sample_rate,n_samples=1)
        self.acquisition_thread.data.connect(self.on_new_data)
        self.acquisition_thread.start()
        self.is_running = True

    def stop_acquisition(self):
        if self.acquisition_thread.is_running:
            self.acquisition_thread.stop()
            self.is_running = False

    def update_plot(self):
        new_data = self.channels_data
        if self.stream_data_option.isChecked():
            try:
                delta = new_data.shape[1] - self.prev_data.shape[1]
                self.plots = np.roll(self.plots, -delta)
                self.plots[::,-delta] = new_data[::,-delta]
            except IndexError:
                delta = new_data.size - self.prev_data.size
                self.plots = np.roll(self.plots, -delta)
                self.plots[-delta:] = new_data[-delta:]
            self.prev_data = new_data
            self.curve.setData(self.plots)

    def on_new_data(self, data):
        try:
            self.channels_data = np.concatenate((self.channels_data,data),axis=1)
        except np.exceptions.AxisError:
            self.channels_data = np.concatenate((self.channels_data,data))