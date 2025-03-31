from PySide6.QtWidgets import(
    QComboBox,
    QDoubleSpinBox,
    QGroupBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget
)
from PySide6.QtCore import Qt
from plot_widgets import ScatterPlotWidget

class SendDataTab(QWidget):
    def __init__(self):
        super().__init__()

        # WIDGETS
        ## LOCK-IN GROUP BOX
        lock_in_group_box = QGroupBox("Lock-In Configuration")
        self.lock_in_address_input = QComboBox()
        self.reference_source_input = QComboBox()
        self.output_amp_input = QDoubleSpinBox()
        self.dynamic_reserve_input = QComboBox()
        self.sensitivity_input = QDoubleSpinBox()
        lock_in_group_box_layout = QVBoxLayout()
        lock_in_group_box_layout.addWidget(QLabel("Instrument Address"))
        lock_in_group_box_layout.addWidget(self.lock_in_address_input)
        lock_in_group_box_layout.addWidget(QLabel("Reference Source"))
        lock_in_group_box_layout.addWidget(self.reference_source_input)
        lock_in_group_box_layout.addWidget(QLabel("Sine Output Amplitude (Vrms)"))
        lock_in_group_box_layout.addWidget(self.output_amp_input)
        lock_in_group_box_layout.addWidget(QLabel("Dynamic Reserve"))
        lock_in_group_box_layout.addWidget(self.dynamic_reserve_input)
        lock_in_group_box_layout.addWidget(QLabel("Sensitivity (V/uA)"))
        lock_in_group_box_layout.addWidget(self.sensitivity_input)
        lock_in_group_box.setLayout(lock_in_group_box_layout)
        ## SWEEP GROUP BOX
        sweep_group_box = QGroupBox("Sweep Parameters")
        self.filename_input = QLineEdit()
        self.f0_input = QDoubleSpinBox()
        self.ff_input = QDoubleSpinBox()
        self.v0_input = QDoubleSpinBox()
        self.vf_input = QDoubleSpinBox()
        self.f_increment_input = QDoubleSpinBox()
        self.v_increment_input = QDoubleSpinBox()
        self.detection_harmonic_number_input = QDoubleSpinBox()
        sweep_group_box_layout = QGridLayout()
        sweep_group_box_layout.addWidget(QLabel("Filename"),0,0,1,1)
        sweep_group_box_layout.addWidget(self.filename_input,0,1,1,1)
        sweep_group_box_layout.addWidget(QLabel("Initial Frequency (Hz)"),1,0,1,1)
        sweep_group_box_layout.addWidget(QLabel("Final Frequency (Hz)"),1,1,1,1)
        sweep_group_box_layout.addWidget(self.f0_input,2,0,1,1)
        sweep_group_box_layout.addWidget(self.ff_input,2,1,1,1)
        sweep_group_box_layout.addWidget(QLabel("Initial Voltage (Vrms)"),3,0,1,1)
        sweep_group_box_layout.addWidget(QLabel("Final Voltage (Vrms)"),3,1,1,1)
        sweep_group_box_layout.addWidget(self.v0_input,4,0,1,1)
        sweep_group_box_layout.addWidget(self.vf_input,4,1,1,1)
        sweep_group_box_layout.addWidget(QLabel("Voltage Increment (Vrms)"),5,0,1,1)
        sweep_group_box_layout.addWidget(QLabel("Frequency Increment (Vrms)"),5,1,1,1)
        sweep_group_box_layout.addWidget(self.v_increment_input,6,0,1,1)
        sweep_group_box_layout.addWidget(self.f_increment_input,6,1,1,1)
        sweep_group_box_layout.addWidget(QLabel("Detection Harmonic Humber"),7,0,1,1)
        sweep_group_box_layout.addWidget(self.detection_harmonic_number_input,7,1,1,1)
        sweep_group_box.setLayout(sweep_group_box_layout)
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
        lock_in_group_box.setFixedWidth(300)
        sweep_group_box.setFixedWidth(300)
        indicators_group_box.setFixedWidth(600)
        self.r_value.setReadOnly(True)
        self.theta_value.setReadOnly(True)
        self.curr_f.setReadOnly(True)
        self.resonance_f.setReadOnly(True)
        self.curr_v.setReadOnly(True)
        self.max_amp.setReadOnly(True)
        self.curr_harmonic.setReadOnly(True)

        

        # LAYOUT
        layout = QGridLayout()
        layout.addWidget(lock_in_group_box,0,0,1,1)
        layout.addWidget(sweep_group_box,0,1,1,1)
        layout.addWidget(indicators_group_box,1,0,1,2)
        layout.addWidget(self.phase_plot_widget,0,2,1,2)
        layout.addWidget(self.amp_plot_widget,1,2,1,2)
        layout.setAlignment(lock_in_group_box,Qt.AlignHCenter)
        layout.setAlignment(sweep_group_box,Qt.AlignHCenter)
        layout.setAlignment(indicators_group_box,Qt.AlignHCenter)
        layout.setAlignment(self.phase_plot_widget,Qt.AlignHCenter)
        layout.setAlignment(self.amp_plot_widget,Qt.AlignHCenter)
        self.setLayout(layout)