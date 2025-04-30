from PySide6.QtWidgets import(
    QDoubleSpinBox,
    QGroupBox,
    QGridLayout,
    QLabel,
    QMessageBox,
    QWidget
)
from PySide6.QtCore import Qt, QThreadPool, QTimer
from plot_widgets import ScatterPlotWidget
from lockin_worker import LockinWorker
from srsinst.sr860 import SR865
from lockin_config_widget import LockInConfigWidget
import pymeasure.instruments.srs.sr830 as SR830
import pyvisa as visa
import numpy as np

class SendDataTab(QWidget):
    def __init__(self):
        super().__init__()

        # WIDGETS
        ## LOCK-IN 1 GROUP BOX
        self.lock_in1_config_widget = LockInConfigWidget(n="1")
        # self.lock_in2_config_widget = LockInConfigWidget(n="2")
        
        ## Indicators Group Box
        indicators_group_box = QGroupBox("Indicators")
        self.r_value = QDoubleSpinBox()
        self.theta_value = QDoubleSpinBox()
        self.curr_f = QDoubleSpinBox()
        self.resonance_f = QDoubleSpinBox()
        self.curr_v = QDoubleSpinBox()
        self.max_amp = QDoubleSpinBox()
        self.curr_harmonic = QDoubleSpinBox()
        indicators_group_box_layout = QGridLayout()
        indicators_group_box_layout.addWidget(QLabel("R value"),0,0,1,1)
        indicators_group_box_layout.addWidget(QLabel("Current Frequency (Hz)"),0,1,1,1)
        indicators_group_box_layout.addWidget(QLabel("Resonance Frequency (Hz)"),0,2,1,1)
        indicators_group_box_layout.addWidget(self.r_value,1,0,1,1)
        indicators_group_box_layout.addWidget(self.curr_f,1,1,1,1)
        indicators_group_box_layout.addWidget(self.resonance_f,1,2,1,1)
        indicators_group_box_layout.addWidget(QLabel("Theta value"),2,0,1,1)
        indicators_group_box_layout.addWidget(QLabel("Current Voltage (V)"),2,1,1,1)
        indicators_group_box_layout.addWidget(QLabel("Max. Amplitude (V)"),2,2,1,1)
        indicators_group_box_layout.addWidget(self.theta_value,3,0,1,1)
        indicators_group_box_layout.addWidget(self.curr_v,3,1,1,1)
        indicators_group_box_layout.addWidget(self.max_amp,3,2,1,1)
        indicators_group_box_layout.addWidget(QLabel("Current Harmonic"),4,1,1,1)
        indicators_group_box_layout.addWidget(self.curr_harmonic,5,1,1,1)
        indicators_group_box.setLayout(indicators_group_box_layout)
        ## PHASE AND AMP PLOTS
        self.phase_plot_widget = ScatterPlotWidget(title="Amplitude vs Frequency", xlabel="Frequency", ylabel="Amplitude")
        self.amp_plot_widget = ScatterPlotWidget(title="Phase vs Frequency", xlabel="Frequency", ylabel="Phase")
        self.phase_plot_widget.setFixedSize(300,300)
        self.amp_plot_widget.setFixedSize(300,300)

        # CONFIG
        self.lock_in1_config_widget.setMaximumSize(500,250)
        # self.lock_in2_config_widget.setFixedWidth(500)
        indicators_group_box.setFixedWidth(600)
        self.r_value.setReadOnly(True)
        self.theta_value.setReadOnly(True)
        self.curr_f.setReadOnly(True)
        self.resonance_f.setReadOnly(True)
        self.curr_v.setReadOnly(True)
        self.max_amp.setReadOnly(True)
        self.curr_harmonic.setReadOnly(True)

        # SIGNALS
        self.lock_in1_config_widget.run_btn.clicked.connect(self.start_sweep)

        # LAYOUT
        layout = QGridLayout()
        layout.addWidget(self.lock_in1_config_widget,0,0,1,6)
        layout.addWidget(indicators_group_box,2,0,1,2)
        layout.addWidget(self.phase_plot_widget,2,2,1,2)
        layout.addWidget(self.amp_plot_widget,2,4,1,2)
        layout.setAlignment(self.lock_in1_config_widget,Qt.AlignHCenter)
        layout.setAlignment(indicators_group_box,Qt.AlignHCenter)
        layout.setAlignment(self.phase_plot_widget,Qt.AlignHCenter)
        layout.setAlignment(self.amp_plot_widget,Qt.AlignHCenter)
        self.setLayout(layout)

        # DATA
        self.fs = np.array([])
        self.thetas = np.array([])
        self.rs = np.array([])

        # THREADPOOL
        self.threadpool = QThreadPool()
        # TIMER
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)

        self.get_visa_resources()

    def get_visa_resources(self):
        resources = visa.ResourceManager().list_resources()
        self.lock_in1_config_widget.address_input.addItems(resources)

    def connect_to_lockin(self, address, v):
        if v == "SR865":
            self.lockin1 = SR865("visa", address)
        elif v == "SR830":
            self.lockin2 = SR830("visa", address)

    def start_sweep(self):
        l1_amp = self.lock_in1_config_widget.output_amp_input.value()
        l1_f0 = self.lock_in1_config_widget.f0_input.value()
        l1_ff = self.lock_in1_config_widget.ff_input.value()
        l1_f_step = self.lock_in1_config_widget.f_step_input.value()
        worker_lockin1 = LockinWorker(lockin=self.lockin1,sine_output=l1_amp,f0=l1_f0,ff=l1_ff,f_step=l1_f_step)
        worker_lockin1.signals.data.connect(self.on_new_data)
        worker_lockin1.signals.finished.connect(self.timer.stop)
        worker_lockin1.signals.failed_connection.connect(lambda: QMessageBox.warning(self, "Connection Error", "No lock-in connection established."))
        self.threadpool.start(worker_lockin1)
        self.timer.start(1000)

    def on_new_data(self, data):
        self.fs = np.append(self.fs,data["f"])
        self.thetas = np.append(self.thetas, data["theta"])
        self.rs = np.append(self.rs, data["r"])

    def update_plots(self):
        self.phase_plot_widget.update_plot(self.fs, self.thetas)
        self.amp_plot_widget.update_plot(self.fs, self.rs)
