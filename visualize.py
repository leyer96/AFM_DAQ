from PySide6.QtWidgets import(
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
    QWidget
)
from PySide6.QtCore import QThreadPool, Qt
from processing_worker import (
    TopographyWorker,
    PFMWorker,
    LVPFMWorker,
    PSDWorker
)
from plot_widgets import CmapWidget, ScatterPlotWidget, SurfacePlotWindowMatplot
import pyqtgraph as pg
import numpy as np

class VisualizeTab(QWidget):
    def __init__(self):
        super().__init__()

        # WIDGETS
        self.study_op = QComboBox()
        self.path_input = QLineEdit()
        self.choose_path_btn = QPushButton("Select Data")
        self.progress_bar = QProgressBar()
        # TOPOGRAPHY OPTIONS
        self.topo_2D_op = QCheckBox("Topo 2D")
        self.topo_3D_op = QCheckBox("Topo 3D (new window)")
        self.topo_profile_line_op = QCheckBox("Topo Profile")
        self.topo_options_btns = [
            self.topo_2D_op,
            self.topo_3D_op,
            self.topo_profile_line_op
        ]
        # PFM OPTIONS
        self.pfm_2D_amp_op = QCheckBox("PFM 2D Amp")
        self.pfm_2D_phase_op = QCheckBox("PFM 2D Phase") 
        self.pfm_3D_amp_op = QCheckBox("PFM 3D Amp (New Window)")
        self.pfm_3D_phase_op = QCheckBox("PFM 3D Phase (New Window)")
        self.pfm_amp_curve_op = QCheckBox("PFM Amp Curve")
        self.pfm_phase_curve_op = QCheckBox("PFM Phase Curve")
        self.pfm_options_btns = [
            self.pfm_2D_amp_op,
            self.pfm_2D_phase_op,
            self.pfm_3D_amp_op,
            self.pfm_3D_phase_op,
            self.pfm_amp_curve_op,
            self.pfm_phase_curve_op
        ]
        # LVPFM OPTIONS
        self.pfm_2D_amp2_op = QCheckBox("PFM 2D Amp - Lateral")
        self.pfm_2D_phase2_op = QCheckBox("PFM 2D Phase - Lateral") 
        self.pfm_3D_amp2_op = QCheckBox("PFM 3D Amp - Lateral (New Window)")
        self.pfm_3D_phase2_op = QCheckBox("PFM 3D Phase - Lateral (New Window)")
        self.pfm_amp2_curve_op = QCheckBox("PFM Amp Curve - Lateral")
        self.pfm_phase2_curve_op = QCheckBox("PFM Phase Curve - Lateral")
        self.pfm_multifreq_options_btns = [
            *self.pfm_options_btns,
            self.pfm_2D_amp2_op,
            self.pfm_2D_phase2_op,
            self.pfm_3D_amp2_op,
            self.pfm_3D_phase2_op,
            self.pfm_amp2_curve_op,
            self.pfm_phase2_curve_op
            ]
        # PLOT WIDGETS
        ## TOPO
        self.topo_cmap_widget = CmapWidget()
        self.topo_x_profile_widget = ScatterPlotWidget(title="X Profile")
        self.topo_y_profile_widget = ScatterPlotWidget(title="Y Profile")
        self.topo_3D_window = None
        ## PFM
        self.v_pfm_groupbox = QGroupBox("Vertical")
        self.pfm_amp_cmap_widget = CmapWidget()
        self.pfm_phase_cmap_widget = CmapWidget()
        self.pfm_phase_curve_widget = ScatterPlotWidget(title="Phase Curve")
        self.pfm_amp_curve_widget = ScatterPlotWidget(title="Amp Curve")
        self.pfm_3D_amp_window = None
        self.pfm_3D_phase_window = None
        ## LVPFM
        self.l_pfm_groupbox = QGroupBox("Lateral")
        self.pfm_amp2_cmap_widget = CmapWidget()
        self.pfm_phase2_cmap_widget = CmapWidget()
        self.pfm_phase2_curve_widget = ScatterPlotWidget(title="Phase Curve")
        self.pfm_amp2_curve_widget = ScatterPlotWidget(title="Amp Curve")
        self.pfm_3D_amp2_window = None
        self.pfm_3D_phase2_window = None
        ## PSD
        self.psd_plot_widget = pg.GraphicsLayoutWidget()
        # CONFIG
        self.progress_bar.hide()
        self.study_op.addItems(["Topography", "PFM", "LVPFM" ,"PSD"])
        self.path_input.setEnabled(False)
        self.topo_2D_op.setChecked(True)
        self.topo_profile_line_op.setChecked(True)
        self.topo_3D_op.setChecked(True)
        self.pfm_amp_cmap_widget.hide()
        self.pfm_amp2_cmap_widget.hide()
        self.pfm_phase_cmap_widget.hide()
        self.pfm_phase2_cmap_widget.hide()
        self.pfm_phase_curve_widget.hide()
        self.pfm_phase2_curve_widget.hide()
        self.pfm_amp_curve_widget.hide()
        self.pfm_amp2_curve_widget.hide()
        self.psd_plot_widget.hide()
        self.v_pfm_groupbox.hide()
        self.l_pfm_groupbox.hide()
        for btn in self.pfm_options_btns:
            btn.hide()
        for btn in self.pfm_multifreq_options_btns:
            btn.hide()

        self.topo_cmap_widget.h_values.connect(lambda values: self.topo_x_profile_widget.update_plot(np.arange(len(values)),values))
        self.topo_cmap_widget.v_values.connect(lambda values: self.topo_y_profile_widget.update_plot(np.arange(len(values)),values))
        self.pfm_amp_cmap_widget.h_values.connect(lambda values: self.pfm_amp_curve_widget.update_plot(np.arange(len(values)),values))
        self.pfm_amp_cmap_widget.v_values.connect(lambda values: self.pfm_amp_curve_widget.update_plot(np.arange(len(values)),values))
        self.pfm_phase_cmap_widget.h_values.connect(lambda values: self.pfm_phase_curve_widget.update_plot(np.arange(len(values)),values))
        self.pfm_phase_cmap_widget.v_values.connect(lambda values: self.pfm_phase_curve_widget.update_plot(np.arange(len(values)),values))
        self.pfm_amp2_cmap_widget.h_values.connect(lambda values: self.pfm_amp2_curve_widget.update_plot(np.arange(len(values)),values))
        self.pfm_amp2_cmap_widget.v_values.connect(lambda values: self.pfm_amp2_curve_widget.update_plot(np.arange(len(values)),values))
        self.pfm_phase2_cmap_widget.h_values.connect(lambda values: self.pfm_phase2_curve_widget.update_plot(np.arange(len(values)),values))
        self.pfm_phase2_cmap_widget.v_values.connect(lambda values: self.pfm_phase2_curve_widget.update_plot(np.arange(len(values)),values))
        
        # THREADPOOL
        self.threadpool = QThreadPool()
        
        # SIGNALS
        self.choose_path_btn.clicked.connect(self.get_pathname)
        self.study_op.currentIndexChanged.connect(self.handle_study_option_change)
        self.topo_profile_line_op.toggled.connect(lambda checked: self.topo_x_profile_widget.show() if checked else self.topo_x_profile_widget.hide())
        self.topo_profile_line_op.toggled.connect(lambda checked: self.topo_y_profile_widget.show() if checked else self.topo_y_profile_widget.hide())
        self.topo_2D_op.toggled.connect(lambda checked: self.topo_cmap_widget.show() if checked else self.topo_cmap_widget.hide())
        self.pfm_2D_amp_op.toggled.connect(lambda checked: self.pfm_amp_cmap_widget.show() if checked else self.pfm_amp_cmap_widget.hide())
        self.pfm_2D_amp2_op.toggled.connect(lambda checked: self.pfm_amp2_cmap_widget.show() if checked else self.pfm_amp2_cmap_widget.hide())
        self.pfm_2D_phase_op.toggled.connect(lambda checked: self.pfm_phase_cmap_widget.show() if checked else self.pfm_phase_cmap_widget.hide())
        self.pfm_2D_phase2_op.toggled.connect(lambda checked: self.pfm_phase2_cmap_widget.show() if checked else self.pfm_phase2_cmap_widget.hide())
        self.pfm_amp_curve_op.toggled.connect(lambda checked: self.pfm_amp_curve_widget.show() if checked else self.pfm_amp_curve_widget.hide())
        self.pfm_amp2_curve_op.toggled.connect(lambda checked: self.pfm_amp2_curve_widget.show() if checked else self.pfm_amp2_curve_widget.hide())
        self.pfm_phase_curve_op.toggled.connect(lambda checked: self.pfm_phase_curve_widget.show() if checked else self.pfm_phase_curve_widget.hide())
        self.pfm_phase2_curve_op.toggled.connect(lambda checked: self.pfm_phase2_curve_widget.show() if checked else self.pfm_phase2_curve_widget.hide())

        # LAYOUT
        layout = QVBoxLayout()

        x_layout1 = QHBoxLayout()
        x_layout1.addWidget(QLabel("Study:"))
        x_layout1.addWidget(self.study_op)

        x_layout2 = QHBoxLayout()
        x_layout2a = QHBoxLayout()
        x_layout2b = QHBoxLayout()
        x_layout2c = QHBoxLayout()
        x_layout2d = QHBoxLayout()

        ## OPTIONS
        x_layout2.addWidget(self.topo_2D_op)
        x_layout2.addWidget(self.topo_3D_op)
        x_layout2.addWidget(self.topo_profile_line_op)
        x_layout2a.addWidget(self.pfm_2D_amp_op)
        x_layout2a.addWidget(self.pfm_2D_phase_op)
        x_layout2a.addWidget(self.pfm_3D_amp_op)
        x_layout2b.addWidget(self.pfm_3D_phase_op)
        x_layout2b.addWidget(self.pfm_amp_curve_op)
        x_layout2b.addWidget(self.pfm_phase_curve_op)
        x_layout2c.addWidget(self.pfm_2D_amp2_op)
        x_layout2c.addWidget(self.pfm_2D_phase2_op)
        x_layout2c.addWidget(self.pfm_3D_amp2_op)
        x_layout2d.addWidget(self.pfm_3D_phase2_op)
        x_layout2d.addWidget(self.pfm_amp2_curve_op)
        x_layout2d.addWidget(self.pfm_phase2_curve_op)

        ## FILE
        x_layout3 = QHBoxLayout()
        x_layout3.addWidget(QLabel("Filename:"))
        x_layout3.addWidget(self.path_input)
        x_layout3.addWidget(self.choose_path_btn)

        ## CMAPS + PSD
        ### LVPFM GROUP BOXES
        #### VERTICAL
        v_pfm_groupbox_layout = QVBoxLayout()
        v_gb_l1 = QHBoxLayout()
        v_gb_l2 = QHBoxLayout()
        v_gb_l1.addWidget(self.pfm_amp_cmap_widget)
        v_gb_l1.addWidget(self.pfm_phase_cmap_widget)
        v_gb_l2.addWidget(self.pfm_amp_curve_widget)
        v_gb_l2.addWidget(self.pfm_phase_curve_widget)
        v_pfm_groupbox_layout.addLayout(v_gb_l1)
        v_pfm_groupbox_layout.addLayout(v_gb_l2)
        self.v_pfm_groupbox.setLayout(v_pfm_groupbox_layout)
        ##### LATERAL
        l_pfm_groupbox_layout = QVBoxLayout()
        l_gb_l1 = QHBoxLayout()
        l_gb_l2 = QHBoxLayout()
        l_gb_l1.addWidget(self.pfm_amp2_cmap_widget)
        l_gb_l1.addWidget(self.pfm_phase2_cmap_widget)
        l_gb_l2.addWidget(self.pfm_amp2_curve_widget)
        l_gb_l2.addWidget(self.pfm_phase2_curve_widget)
        l_pfm_groupbox_layout.addLayout(l_gb_l1)
        l_pfm_groupbox_layout.addLayout(l_gb_l2)
        self.l_pfm_groupbox.setLayout(l_pfm_groupbox_layout)

        x_layout4 = QHBoxLayout()
        x_layout4.addWidget(self.topo_cmap_widget)
        x_layout4.addWidget(self.psd_plot_widget)
        x_layout4.addWidget(self.v_pfm_groupbox)
        x_layout4.addWidget(self.l_pfm_groupbox)
        
        ## TOPO PROFILE LINES
        x_layout5 = QHBoxLayout()
        x_layout5.addWidget(self.topo_x_profile_widget)
        x_layout5.addWidget(self.topo_y_profile_widget)

        layout.addLayout(x_layout1)
        layout.addLayout(x_layout2)
        layout.addLayout(x_layout2a)
        layout.addLayout(x_layout2b)
        layout.addLayout(x_layout2c)
        layout.addLayout(x_layout2d)
        layout.addLayout(x_layout3)
        layout.addWidget(self.progress_bar)
        layout.addLayout(x_layout4)
        layout.addLayout(x_layout5)
        self.setLayout(layout)

        

    def handle_study_option_change(self, index):
        self.path_input.clear()
        btns_list = [
            self.topo_options_btns,
            self.pfm_options_btns,
            self.pfm_multifreq_options_btns
        ]
        for i in range(len(btns_list)):
            btns = btns_list[i]
            if i == index:
                for btn in btns:
                    btn.show()
                    btn.setChecked(True)
            else:
                for btn in btns:
                    if index == 1 and btn in self.pfm_multifreq_options_btns[0:6]:
                        continue
                    btn.hide()
                    btn.setChecked(False)
        self.psd_plot_widget.show() if index == 3 else self.psd_plot_widget.hide()
        self.v_pfm_groupbox.show() if index == 1 or index == 2 else self.v_pfm_groupbox.hide()
        self.l_pfm_groupbox.show() if index == 2 else self.l_pfm_groupbox.hide()
    
    def get_pathname(self):
        path_data = QFileDialog.getOpenFileName(caption=f"SELECT {self.study_op.currentText()} DATAFILE")
        path = path_data[0]
        if path:
            self.path_input.setText(path)
            self.prepare_for_plotting(path)

    def prepare_for_plotting(self,path):
        op = self.study_op.currentText()
        self.study_op.setEnabled(False)
        self.choose_path_btn.setEnabled(False)
        self.progress_bar.show()
        if op == "Topography":
            worker = TopographyWorker(path)    
        elif op == "PFM":
            worker = PFMWorker(path)
        elif op == "LVPFM":
            worker = LVPFMWorker(path)
        elif op == "PSD":
            worker = PSDWorker(path)
        worker.signals.data.connect(self.create_plots)
        worker.signals.error.connect(self.handle_error)
        worker.signals.progress.connect(self.update_progress_bar)
        self.threadpool.start(worker)

    def update_progress_bar(self, n):
        self.progress_bar.setValue(n)
    
    def handle_error(self, err):
        self.study_op.setEnabled(True)
        self.choose_path_btn.setEnabled(True)
        self.progress_bar.reset()
        self.progress_bar.hide()
        QMessageBox.critical(self, "Processing Error", f"An error ({err}) has occurred while processing the data. Try with a new set.")
    
    def create_plots(self, data):
        self.progress_bar.reset()
        self.progress_bar.hide()
        op = self.study_op.currentText()
        if op == "Topography":
            Z = data
            zlabel_3d = "Height (V)"
            self.topo_x_profile_widget.set_ylabel("Height (V)")
            self.topo_y_profile_widget.set_ylabel("Height (V)")
            if self.topo_2D_op.isChecked():
                self.topo_cmap_widget.setup_widget(Z)
            if self.topo_3D_op.isChecked():
                self.topo_3D_window = SurfacePlotWindowMatplot(Z,title="Topography",xlabel="Pixel",ylabel="Pixel",zlabel=zlabel_3d)
                self.topo_3D_window.show()
        elif op == "PFM":
            amp_and_phase = data
            amp = amp_and_phase[0,:]
            phase = amp_and_phase[1,:]
            if self.pfm_2D_amp_op.isChecked():
                self.pfm_amp_cmap_widget.setup_widget(amp)
            if self.pfm_2D_phase_op.isChecked():
                self.pfm_phase_cmap_widget.setup_widget(phase)
            if self.pfm_3D_amp_op.isChecked():
                self.pfm_3D_amp_window = SurfacePlotWindowMatplot(
                    amp,
                    title="Amplitude Image",
                    xlabel="Pixel",ylabel="Pixel",zlabel="Amplitude (V)")
                self.pfm_3D_amp_window.show()
            if self.pfm_3D_phase_op.isChecked():
                self.pfm_3D_phase_window = SurfacePlotWindowMatplot(
                    phase,
                    title="Phase Image",xlabel="Pixel",ylabel="Pixel",zlabel="Phase (Deg.)")
                self.pfm_3D_phase_window.show()
        elif op == "LVPFM":
            amps_and_phases = data
            amp = amps_and_phases[0,:] 
            phase = amps_and_phases[1,:]
            amp2 = amps_and_phases[2,:] 
            phase2 = amps_and_phases[3,:]
            if self.pfm_2D_amp_op.isChecked():
                self.pfm_amp_cmap_widget.setup_widget(amp)
            if self.pfm_2D_phase_op.isChecked():
                self.pfm_phase_cmap_widget.setup_widget(phase)
            if self.pfm_3D_amp_op.isChecked():
                self.pfm_3D_amp_window = SurfacePlotWindowMatplot(
                    amp,
                    title="Amplitude Image",
                    xlabel="Pixel",ylabel="Pixel",zlabel="Amplitude (V)")
                self.pfm_3D_amp_window.show()
            if self.pfm_3D_phase_op.isChecked():
                self.pfm_3D_phase_window = SurfacePlotWindowMatplot(
                    phase,
                    title="Phase Image",xlabel="Pixel",ylabel="Pixel",zlabel="Phase (Deg.)")
                self.pfm_3D_phase_window.show()
            if self.pfm_2D_amp2_op.isChecked():
                self.pfm_amp2_cmap_widget.setup_widget(amp2)
            if self.pfm_2D_phase2_op.isChecked():
                self.pfm_phase2_cmap_widget.setup_widget(phase2)
            if self.pfm_3D_amp2_op.isChecked():
                self.pfm_3D_amp2_window = SurfacePlotWindowMatplot(
                    amp2,
                    title="Amplitude Image (Lateral)",
                    xlabel="Pixel",ylabel="Pixel",zlabel="Amplitude (V)")
                self.pfm_3D_amp2_window.show()
            if self.pfm_3D_phase2_op.isChecked():
                self.pfm_3D_phase2_window = SurfacePlotWindowMatplot(
                    phase2,
                    title="Phase Image (Lateral)",
                    xlabel="Pixel",ylabel="Pixel",zlabel="Amplitude (V)")
                self.pfm_3D_phase2_window.show()
        elif op == "PSD":
            frequencies = data["fs"]
            psd = data["psd"]
            noise = data["noise"]
            k = data["k"]
            x = np.arange(1,noise.size+1)
            noise_plot = self.psd_plot_widget.addPlot(row=0,col=0,x=x,y=noise,units="V")
            noise_plot.setLabel('top', 'Data Number')
            noise_plot.setLabel('left', 'Voltage', units='V')
            self.psd_plot_widget.addLabel(f"Spring K constant: {np.round(k,4)}",row=1,col=0)
            psd_plot = self.psd_plot_widget.addPlot(row=2,col=0,x=frequencies,y=psd,units="Hz")
            psd_plot.setLabel('bottom', 'Frequency', units='Hz')
            psd_plot.setLabel('left', 'Amplitude', units='V')
        self.study_op.setEnabled(True)
        self.choose_path_btn.setEnabled(True)

    def detrend_data(self):
        try:
            op = self.study_op.currentText()
            if op == "Topography":
                if self.topo_2D_op.isChecked():
                    self.topo_cmap_widget.detrend_image()
                if self.topo_3D_op.isChecked():
                    self.topo_3D_window.detrend_image()
            elif op == "PFM":
                if self.pfm_2D_amp_op.isChecked():
                    self.pfm_amp_cmap_widget.detrend_image()
                if self.pfm_2D_phase_op.isChecked():
                    self.pfm_phase_cmap_widget.detrend_image()
                if self.pfm_3D_amp_op.isChecked():
                    self.pfm_3D_amp_window.detrend_image()
                if self.pfm_3D_phase_op.isChecked():
                    self.pfm_3D_phase_window.detrend_image()
            elif op == "LVPFM":
                if self.pfm_2D_amp_op.isChecked():
                    self.pfm_amp_cmap_widget.detrend_image()
                if self.pfm_2D_phase_op.isChecked():
                    self.pfm_phase_cmap_widget.detrend_image()
                if self.pfm_3D_amp_op.isChecked():
                    self.pfm_3D_amp_window.detrend_image()
                if self.pfm_3D_phase_op.isChecked():
                    self.pfm_3D_phase_window.detrend_image()
                if self.pfm_2D_amp2_op.isChecked():
                    self.pfm_amp2_cmap_widget.detrend_image()
                if self.pfm_3D_amp2_op.isChecked():
                    self.pfm_3D_amp2_window.detrend_image()
                if self.pfm_3D_phase2_op.isChecked():
                    self.pfm_3D_phase2_window.detrend_image()
        except AttributeError as e:
            QMessageBox.information(self, "Invalid operation","Operation not available")

    def go_back(self):
        try:
            op = self.study_op.currentText()
            if op == "Topography":
                if self.topo_2D_op.isChecked():
                    self.topo_cmap_widget.go_back()
                if self.topo_3D_op.isChecked():
                    self.topo_3D_window.go_back()
            elif op == "PFM":
                if self.pfm_2D_amp_op.isChecked():
                    self.pfm_amp_cmap_widget.go_back()
                if self.pfm_2D_phase_op.isChecked():
                    self.pfm_phase_cmap_widget.go_back()
                if self.pfm_3D_amp_op.isChecked():
                    self.pfm_3D_amp_window.go_back()
                if self.pfm_3D_phase_op.isChecked():
                    self.pfm_3D_phase_window.go_back()
            elif op == "LVPFM":
                if self.pfm_2D_amp_op.isChecked():
                    self.pfm_amp_cmap_widget.go_back()
                if self.pfm_2D_phase_op.isChecked():
                    self.pfm_phase_cmap_widget.go_back()
                if self.pfm_3D_amp_op.isChecked():
                    self.pfm_3D_amp_window.go_back()
                if self.pfm_3D_phase_op.isChecked():
                    self.pfm_3D_phase_window.go_back()
                if self.pfm_2D_amp2_op.isChecked():
                    self.pfm_amp2_cmap_widget.go_back()
                if self.pfm_3D_amp2_op.isChecked():
                    self.pfm_3D_amp2_window.go_back()
                if self.pfm_3D_phase2_op.isChecked():
                    self.pfm_3D_phase2_window.go_back()
        except AttributeError as e:
            print(e)
            QMessageBox.information(self, "Invalid operation","Operation not available")

    def add_sensitivity_rate(self):
        sensitivity_rate, ok = QInputDialog.getDouble(
                self,
                "Sensitivity rate",
                "Sensitivity rate (V/nm):",
                value=0,
                minValue=0,
                maxValue=2000,
                decimals=2,
                )
        if ok and sensitivity_rate:
            if self.topo_2D_op.isChecked():
                self.topo_cmap_widget.set_sensitivity_rate(sensitivity_rate)
            if self.topo_3D_op.isChecked():
                self.topo_3D_window.set_sensitivity_rate(sensitivity_rate)
            if self.topo_profile_line_op.isChecked():
                self.topo_x_profile_widget.set_ylabel("Height (nm)")
                self.topo_y_profile_widget.set_ylabel("Height (nm)")