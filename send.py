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
# from srsinst.sr860 import SR865
# from pymeasure.instruments.srs import SR830
from lockin_config_widget import LockInConfigWidget
# import pyvisa as visa
import numpy as np

class SendDataTab(QWidget):
    def __init__(self):
        super().__init__()

        # WIDGETS
        ## LOCK-IN 1 GROUP BOX
        self.lock_in1_config_widget = LockInConfigWidget(n="1")
        
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
        indicators_group_box_layout.addWidget(QLabel("Max. Amplitude (mV)"),2,2,1,1)
        indicators_group_box_layout.addWidget(self.theta_value,3,0,1,1)
        indicators_group_box_layout.addWidget(self.curr_v,3,1,1,1)
        indicators_group_box_layout.addWidget(self.max_amp,3,2,1,1)
        indicators_group_box_layout.addWidget(QLabel("Current Harmonic"),4,1,1,1)
        indicators_group_box_layout.addWidget(self.curr_harmonic,5,1,1,1)
        indicators_group_box.setLayout(indicators_group_box_layout)
        ## PHASE AND AMP PLOTS
        self.phase_plot_widget = ScatterPlotWidget(title="Phase vs Frequency", xlabel="Frequency", ylabel="Amplitude",xunits="Hz",yunits="Deg.")
        self.amp_plot_widget = ScatterPlotWidget(title="Amplitude vs Frequency", xlabel="Frequency", ylabel="Phase",xunits="Hz",yunits="V")
        self.phase_plot_widget.setFixedSize(300,300)
        self.amp_plot_widget.setFixedSize(300,300)

        # CONFIG
        self.lock_in1_config_widget.setMaximumSize(500,250)
        indicators_group_box.setFixedWidth(600)
        self.r_value.setReadOnly(True)
        self.theta_value.setReadOnly(True)
        self.curr_f.setReadOnly(True)
        self.resonance_f.setReadOnly(True)
        self.curr_v.setReadOnly(True)
        self.max_amp.setReadOnly(True)
        self.curr_harmonic.setReadOnly(True)
        self.r_value.setRange(-1E4,1E4)
        self.theta_value.setRange(-1E4,1E4)
        self.curr_f.setRange(-1E10,1E10)
        self.resonance_f.setRange(-1E10,1E10)
        self.curr_v.setRange(-1E4,1E4)
        self.max_amp.setRange(-1E4,1E4)
        self.curr_harmonic.setRange(0,1E4)
        self.curr_f.setGroupSeparatorShown(True)
        self.resonance_f.setGroupSeparatorShown(True)

        # SIGNALS
        self.lock_in1_config_widget.run_btn.clicked.connect(self.start_sweep)
        self.lock_in1_config_widget.stop_btn.clicked.connect(self.stop_sweep)
        self.lock_in1_config_widget.address_input.currentTextChanged.connect(self.connect_to_lockin)

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

        # self.get_visa_resources()

    def get_visa_resources(self):
        resources = visa.ResourceManager().list_resources()
        self.lock_in1_config_widget.address_input.addItems(resources)

    def connect_to_lockin(self, address):
        if address.startswith("GPIB"):
            self.lockin = SR830(address)
        else:
            self.lockin = SR865("visa", address)

    def start_sweep(self):
        l1_amp = self.lock_in1_config_widget.output_amp_input.value()
        l1_f0 = self.lock_in1_config_widget.f0_input.value()
        l1_ff = self.lock_in1_config_widget.ff_input.value()
        l1_f_step = self.lock_in1_config_widget.f_step_input.value()
        self.fs = np.array([])
        self.rs = np.array([])
        self.thetas = np.array([])
        self.worker_lockin = LockinWorker(lockin=self.lockin,sine_output=l1_amp,f0=l1_f0,ff=l1_ff,f_step=l1_f_step)
        self.worker_lockin.signals.data.connect(self.on_new_data)
        self.worker_lockin.signals.finished.connect(self.handle_finish)
        self.worker_lockin.signals.failed_connection.connect(lambda: QMessageBox.warning(self, "Connection Error", "No lock-in connection established."))
        self.threadpool.start(self.worker_lockin)
        self.timer.start(500)

    def on_new_data(self, data):
        f = data["f"]
        theta = data["theta"]
        r = data["r"]
        self.fs = np.append(self.fs,f)
        self.thetas = np.append(self.thetas, theta)
        self.rs = np.append(self.rs, r)
        self.r_value.setValue(r)
        self.theta_value.setValue(theta)
        self.curr_f.setValue(f)

    def update_plots(self):
        self.phase_plot_widget.update_plot(self.fs, self.thetas)
        self.amp_plot_widget.update_plot(self.fs, self.rs)

    def handle_finish(self):
        max_amp = np.max(self.rs)*1000
        idx = np.argmax(self.rs)
        res_f = self.fs[idx]
        self.max_amp.setValue(max_amp)
        self.resonance_f.setValue(res_f)
        self.timer.stop()
        self.update_plots()

    def stop_sweep(self):
        self.worker_lockin.running = False
        self.handle_finish()
        