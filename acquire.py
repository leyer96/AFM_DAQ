from PySide6.QtWidgets import(
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget
)
from PySide6.QtCore import QTimer, QThreadPool
from PySide6.QtGui import QIcon
from acquisition_thread import AcquisitionThread
from recording_thread import RecordingThread
from recording_worker import RecordingWorker
from utils import Paths, CHANNELS_NAMES, STYLES
import pyqtgraph as pg
import numpy as np
from datetime import datetime
import shutil
import queue
import time


class AcquireTab(QWidget):
    def __init__(self):
        super().__init__()
        # ---- WIDGETS ---- #
        ## PLOT WIDGET
        self.plot_widget = pg.PlotWidget()
        self.stream_data_option = QCheckBox("Stream data")
        ## PLOT CONFIG
        acquisition_config_group_box = QGroupBox("Plot Configuration")
        self.channel_selection_input = QComboBox()
        ## DAQ CONFIG
        daq_config_group_box = QGroupBox("DAQ Configuration")
        self.n_channels_input = QSpinBox() 
        self.min_input_value_input = QDoubleSpinBox()
        self.max_input_value_input = QDoubleSpinBox()
        self.sample_rate_input = QSpinBox()
        self.n_samples_input = QSpinBox()
        ## RECORDING CONTROLS
        self.record_btn = QPushButton("RECORD")
        stop_btn = QPushButton("STOP")
        
        # ---- DATA ---- #
        self.channels_data = np.array([])
        self.plot_data = np.zeros(50000)
        self.plots_refs = [self.plot_widget.plot(np.array([]), pen="yellow")] # CREAR PEN ANTES
        self.buffer = queue.Queue()

        # ---- CONFIG ---- #
        self.is_recording = False
        self.is_streaming = False
        ## THREADS & TIMER
        self.threadpool = QThreadPool()
        self.plot_timer = QTimer(self)
        self.plot_timer.timeout.connect(self.update_plot)
        ## INPUTS
        self.n_channels_input.setRange(1,8)
        self.n_channels_input.setValue(1)
        self.channel_selection_input.addItem("All")
        self.sample_rate_input.setRange(0,1.5E6)
        self.sample_rate_input.setValue(40_000)
        self.sample_rate_input.setGroupSeparatorShown(True)
        self.min_input_value_input.setRange(-10,10)
        self.min_input_value_input.setValue(-10)
        self.max_input_value_input.setRange(-10,10)
        self.max_input_value_input.setValue(10)
        self.n_samples_input.setRange(0,1.5E6)
        self.n_samples_input.setValue(40_000)
        self.n_samples_input.setGroupSeparatorShown(True)
        ## ICONS
        self.record_btn.setIcon(QIcon(Paths.icon("control-record.png")))
        stop_btn.setIcon(QIcon(Paths.icon("control-stop-square.png")))
        ## STYLE
        self.record_btn.setStyleSheet(STYLES["btn"])
        stop_btn.setStyleSheet(STYLES["btn"])
        # ---- SIGNALS ---- #
        self.stream_data_option.toggled.connect(self.toggle_stream)
        self.n_channels_input.valueChanged.connect(self.set_n_of_channels)
        self.min_input_value_input.valueChanged.connect(self.set_max_input)
        self.channel_selection_input.currentIndexChanged.connect(self.change_plots_visibility)
        self.record_btn.clicked.connect(lambda: self.start_acquisition(mode="WRITE"))
        self.sample_rate_input.valueChanged.connect(self.handle_sample_rate_input_change)
        stop_btn.clicked.connect(self.stop_recording)

        # ---- LAYOUT ---- #
        ## FORM - DAQ CONFIG
        f1 = QFormLayout()
        f1.addRow("Plot channel", self.channel_selection_input)
        acquisition_config_group_box.setLayout(f1)
        f2 = QFormLayout()
        f2.addRow("# of channels to acquire", self.n_channels_input)
        f2.addRow("Min. Value (V)", self.min_input_value_input)
        f2.addRow("Max. Value (V)", self.max_input_value_input)
        f2.addRow("DAQ Sample Rate (samples/s)", self.sample_rate_input)
        f2.addRow("Number of Samples (samples per read)", self.n_samples_input)
        daq_config_group_box.setLayout(f2)
        ## MAIN LAYOUT
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        layout.addWidget(self.stream_data_option)
        h_l1 = QHBoxLayout()
        h_l1.addWidget(acquisition_config_group_box)
        h_l1.addWidget(daq_config_group_box)
        layout.addLayout(h_l1)
        layout.addWidget(self.record_btn)
        layout.addWidget(stop_btn)

        self.setLayout(layout)

    def set_n_of_channels(self,n):
        arr = [[] for _ in range(n)]
        self.channels_data = np.array(arr)
        samp_r = self.sample_rate_input.value()
        if n == 1:
            self.plot_data = np.zeros(samp_r)
        else:
            self.plot_data = np.zeros((n,samp_r))
        pens = ["yellow","green","blue","red","white","pink","orange","gray"]
        for plot_ref in self.plots_refs:
            self.plot_widget.removeItem(plot_ref)
        self.plots_refs = [self.plot_widget.plot(np.array([]), pen=pens[i]) for i in range(n)]
        self.channel_selection_input.clear()
        self.channel_selection_input.addItem("All")
        self.channel_selection_input.addItems(CHANNELS_NAMES[0:n])

    def handle_sample_rate_input_change(self, samp_r):
        n = self.n_channels_input.value()
        self.n_samples_input.setRange(0,samp_r)
        self.n_samples_input.setValue(samp_r)
        if n == 1:
            self.plot_data = np.zeros(samp_r)
        else:
            self.plot_data = np.zeros((n,samp_r))

    def set_max_input(self,min_v):
        self.max_input_value_input.setMinimum(min_v)

    def toggle_stream(self, checked):
        if checked:
            self.start_acquisition()
        else:
            self.stop_acquisition()
    
    def start_acquisition(self,mode="READ"):
        n_channels = self.n_channels_input.value()
        min_v = self.min_input_value_input.value()
        max_v = self.max_input_value_input.value()
        sample_rate = self.sample_rate_input.value()
        n_samples = self.n_samples_input.value()
        self.plot_timer.start(1000)
        if mode == "READ":
            self.acquisition_thread = AcquisitionThread(n_channels=n_channels,min_v=min_v,max_v=max_v,sample_rate=sample_rate,n_samples=n_samples)
        elif mode == "WRITETOREAD":
            self.acquisition_thread.stop()
            time.sleep(0.5)
            self.acquisition_thread = AcquisitionThread(n_channels=n_channels,min_v=min_v,max_v=max_v,sample_rate=sample_rate,n_samples=n_samples)
        elif mode == "WRITE":
            self.acquisition_thread.stop()
            time.sleep(0.5)
            self.record_btn.setEnabled(False)
            self.acquisition_thread = RecordingThread(n_channels=n_channels,min_v=min_v,max_v=max_v,sample_rate=sample_rate,n_samples=n_samples)
        self.acquisition_thread.data.connect(self.on_new_data)
        self.acquisition_thread.start()
        self.is_streaming = True
        self.n_channels_input.setEnabled(False)
        self.sample_rate_input.setEnabled(False)
        self.n_samples_input.setEnabled(False)
        self.min_input_value_input.setEnabled(False)
        self.max_input_value_input.setEnabled(False)

    def stop_acquisition(self):
        if self.is_streaming:
            self.acquisition_thread.stop()
            self.plot_timer.stop()
            self.is_streaming = False
            self.n_channels_input.setEnabled(True)
            self.sample_rate_input.setEnabled(True)
            self.n_samples_input.setEnabled(True)
            self.min_input_value_input.setEnabled(True)
            self.max_input_value_input.setEnabled(True)
            self.record_btn.setEnabled(True)


    def stop_recording(self):
        self.record_btn.setEnabled(True)
        self.start_acquisition(mode="WRITETOREAD")
        dirname = QFileDialog().getExistingDirectory()
        if dirname:
            dlg = FileNameDialog(dirname)
            dlg.exec()


    def update_plot(self):
        if self.stream_data_option.isChecked():
            if len(self.plots_refs) == 1:
                self.plots_refs[0].setData(self.plot_data)
            else:
                for i in range(len(self.plots_refs)):
                    self.plots_refs[i].setData(self.plot_data[i,:])

    def on_new_data(self, new_data):
        if new_data.ndim == 2:
            n = new_data.shape[1]
            if new_data.shape[0] > 1:
                self.plot_data = np.roll(self.plot_data,-n,axis=1)
                self.plot_data[:,-n:] = new_data
        else:
            n = new_data.shape[0]
            self.plot_data = np.roll(self.plot_data,-n)
            self.plot_data[-n:] = new_data

    def change_plots_visibility(self, index):
        if index == 0:
            for plot_ref in self.plots_refs:
                plot_ref.setVisible(True)
        else:
            index -= 1
            for idx,plot_ref in enumerate(self.plots_refs):
                if idx != index:
                    plot_ref.setVisible(False)
                else:
                    plot_ref.setVisible(True)


class FileNameDialog(QDialog):
    def __init__(self, dirname):
        super().__init__()
        self.dirname = dirname

        self.filename_input = QLineEdit()
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)

        now_str = datetime.now().strftime("%H:%m-%d-%M-%Y")
        
        button_box.accepted.connect(self.save_file)

        self.filename_input.setText(f"{now_str}_ADM_DAQ_data")

        layout = QVBoxLayout()
        layout.addWidget(self.filename_input)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def save_file(self):
        filename = self.filename_input.text()
        if filename:
            src = "./recording.tdms"
            destination = self.dirname + "/" + filename + ".tdms"
            shutil.move(src,destination)
            self.close()