from threading import Thread
from PySide6.QtWidgets import(
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from acquisition_thread import AcquisitionThread
from widgets import ConnectionStatusIndicator
from utils import Paths
import pyqtgraph as pg
import numpy as np
import pandas as pd


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
        self.record_btn = QPushButton("RECORD")
        stop_btn = QPushButton("STOP")
        
        # ---- DATA ---- #
        self.channels_data = np.array([])
        self.plot_data = np.zeros(100)
        self.plots_refs = [self.plot_widget.plot(np.array([]), pen="y")] # CREAR PEN ANTES

        # ---- CONFIG ---- #
        self.DAQ_connected = False
        self.is_recording = False
        ## THREADS & TIMER
        self.plot_timer = QTimer(self)
        self.plot_timer.timeout.connect(self.update_plot)
        self.plot_timer.start(100)
        ## PLOT
        self.plot_widget.setXRange(1,100)
        self.plot_widget.setYRange(-0.4,0.4)
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
        self.record_btn.setIcon(QIcon(Paths.icon("control-record.png")))
        stop_btn.setIcon(QIcon(Paths.icon("control-stop-square.png")))

        # ---- SIGNALS ---- #
        self.stream_data_option.toggled.connect(self.toggle_stream)
        self.n_channels_input.valueChanged.connect(self.set_n_of_channels)
        self.min_input_value_input.valueChanged.connect(self.set_max_input)
        self.record_btn.clicked.connect(self.start_recording)
        stop_btn.clicked.connect(self.stop_recording)

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
        layout.addWidget(self.record_btn)
        layout.addWidget(stop_btn)

        self.setLayout(layout)
        
        # ---- TEST ---- #

        # ----- TEST -----

    def set_n_of_channels(self,n):
        arr = [[] for _ in range(n)]
        self.channels_data = np.array(arr)
        self.plot_data = np.zeros((n,100)) # CAMBIAR
        colors = ["y","g","b","r"]
        self.plots_refs = [self.plot_widget.plot(np.array([]), pen=colors[i]) for i in range(n)]

    def set_max_input(self,min_v):
        self.max_input_value_input.setMinimum(min_v)

    def toggle_stream(self, checked):
        if checked:
            self.start_acquisition()
        else:
            self.stop_acquisition()
    
    def start_acquisition(self):
        n_channels = self.n_channels_input.value()
        min_v = self.min_input_value_input.value()
        max_v = self.max_input_value_input.value()
        sample_rate = self.sample_rate_input.value()
        n_samples = self.n_samples_input.value()
        self.acquisition_thread = AcquisitionThread(n_channels=n_channels,min_v=min_v,max_v=max_v,sample_rate=sample_rate,n_samples=1)
        self.acquisition_thread.data.connect(self.on_new_data)
        self.acquisition_thread.start()

    def stop_acquisition(self):
        try:
            self.acquisition_thread.stop()
        except:
            pass

    def start_recording(self):
        self.is_recording = True
        self.record_btn.setEnabled(False)

    def stop_recording(self):
        # TEST 
        self.is_recording = False
        cols = ["Dev1/ai"+str(i) for i in range(len(self.plots_refs))]
        data = self.channels_data.T
        df = pd.DataFrame(data,columns=cols)
        fn = "test.csv"
        dirname = QFileDialog.getExistingDirectory(self)
        if dirname:
            path = dirname + fn
            df.to_csv(path,index=False)
        n = self.n_channels_input.value()
        self.channels_data = np.array([[] for _ in range(n)])
        self.record_btn.setEnabled(True)

    def update_plot(self):
        if self.stream_data_option.isChecked():
            if len(self.plots_refs) == 1:
                self.plots_refs[0].setData(self.plot_data)
            else:
                for i in range(len(self.plots_refs)):
                    self.plots_refs[i].setData(self.plot_data[i,:])

    def on_new_data(self, new_data):
        n = len(new_data)
        new_data = np.array(new_data)
        if new_data.shape[0] == 1:
            self.plot_data = np.roll(self.plot_data, -n)
            self.plot_data[-n:] = new_data
            if self.is_recording:
                 self.channels_data = np.concatenate((self.channels_data,new_data))
        else:
            self.plot_data = np.roll(self.plot_data, -n,axis=1)
            self.plot_data[:,-n:] = new_data
            if self.is_recording:
                self.channels_data = np.concatenate((self.channels_data,new_data),axis=1)