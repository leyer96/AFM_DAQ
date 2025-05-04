from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

class LockInConfigWidget(QWidget):
    def __init__(self, n="1"):
        super().__init__()
        #WIDGETS
        group_box = QGroupBox(f"Lock-In {n} Configuration")
        self.address_input = QComboBox()
        self.output_amp_input = QDoubleSpinBox()
        self.f0_input = QDoubleSpinBox()
        self.ff_input = QDoubleSpinBox()
        self.f_step_input = QDoubleSpinBox()
        self.run_btn = QPushButton("Run")
        self.stop_btn = QPushButton("Stop")
        # LAYOUT
        form = QFormLayout()
        form.addRow("Instrument Address", self.address_input)
        form.addRow("Sine Output Amplitude (Vrms)", self.output_amp_input)
        form.addRow("Initial Frequency (Hz.)", self.f0_input)
        form.addRow("Final Frequency (Hz.)", self.ff_input)
        form.addRow("Frequency Step (Hz.)", self.f_step_input)
        form.addRow("",self.run_btn)
        form.addRow("",self.stop_btn)

        group_box.setLayout(form)
        layout = QVBoxLayout()
        layout.addWidget(group_box)
        self.setLayout(layout)

        # CONFIG
        self.address_input.addItem("-- Select --")
        self.f0_input.setRange(0,1e6)
        self.ff_input.setRange(0,1e6)
        self.f_step_input.setRange(0,1e6)
        self.output_amp_input.setRange(0,2)
        self.f0_input.setValue(1e3)
        self.ff_input.setValue(2e3)
        self.f_step_input.setValue(50)
        self.output_amp_input.setValue(1)