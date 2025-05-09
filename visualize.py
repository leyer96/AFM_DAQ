from PySide6.QtWidgets import(
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
    QWidget
)
from PySide6.QtCore import QThreadPool
from processing_worker import ProcessingWorker
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
        # PFM - MULTIFREQ OPTIONS
        self.pfm_2D_amp2_op = QCheckBox("PFM 2D Amp - Lateral")
        self.pfm_2D_phase2_op = QCheckBox("PFM 2D Phase - Lateral") 
        self.pfm_3D_amp2_op = QCheckBox("PFM 3D Amp - Lateral (New Window)")
        self.pfm_3D_phase2_op = QCheckBox("PFM 3D Phase - Lateral (New Window)")
        self.pfm_amp2_curve_op = QCheckBox("PFM Amp Curve")
        self.pfm_phase2_curve_op = QCheckBox("PFM Phase Curve")
        self.pfm_multifreq_options_btns = [
            *self.pfm_options_btns,
            self.pfm_2D_amp2_op,
            self.pfm_2D_phase2_op,
            self.pfm_3D_amp2_op,
            self.pfm_3D_phase2_op,
            self.pfm_amp2_curve_op,
            self.pfm_phase2_curve_op
            ]
        # PLOT WIDGETSs
        self.topo_cmap_widget = CmapWidget()
        self.pfm_amp_cmap_widget = CmapWidget()
        self.pfm_amp2_cmap_widget = CmapWidget()
        self.pfm_phase_cmap_widget = CmapWidget()
        self.pfm_phase2_cmap_widget = CmapWidget()
        self.topo_x_profile_widget = ScatterPlotWidget(title="X Profile")
        self.topo_y_profile_widget = ScatterPlotWidget(title="Y Profile")
        self.pfm_phase_curve_widget = ScatterPlotWidget(title="Phase Curve")
        self.pfm_amp_curve_widget = ScatterPlotWidget(title="Amp Curve")
        self.pfm_phase2_curve_widget = ScatterPlotWidget(title="Phase Curve")
        self.pfm_amp2_curve_widget = ScatterPlotWidget(title="Amp Curve")
        self.psd_plot_widget = pg.GraphicsLayoutWidget()
        self.topo_3D_window = None
        self.pfm_3D_amp_window = None
        self.pfm_3D_phase_window = None
        self.pfm_3D_amp2_window = None
        self.pfm_3D_phase2_window = None
        # CONFIG
        self.progress_bar.hide()
        self.study_op.addItems(["Topography", "PFM", "PFM - MultiFreq" ,"PSD"])
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

        x_layout3 = QHBoxLayout()
        x_layout3.addWidget(QLabel("Filename:"))
        x_layout3.addWidget(self.path_input)
        x_layout3.addWidget(self.choose_path_btn)

        x_layout4 = QHBoxLayout()
        x_layout4.addWidget(self.topo_cmap_widget)
        x_layout4.addWidget(self.pfm_amp_cmap_widget)
        x_layout4.addWidget(self.pfm_phase_cmap_widget)
        x_layout4.addWidget(self.pfm_amp2_cmap_widget)
        x_layout4.addWidget(self.pfm_phase2_cmap_widget)
        x_layout4.addWidget(self.psd_plot_widget)
        
        x_layout5 = QHBoxLayout()
        x_layout5.addWidget(self.topo_x_profile_widget)
        x_layout5.addWidget(self.topo_y_profile_widget)
        x_layout5.addWidget(self.pfm_amp_curve_widget)
        x_layout5.addWidget(self.pfm_phase_curve_widget)
        x_layout5.addWidget(self.pfm_amp2_curve_widget)
        x_layout5.addWidget(self.pfm_phase2_curve_widget)

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
        if index == 3:
            self.psd_plot_widget.show()
        else:
            self.psd_plot_widget.hide()
    
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
        worker = ProcessingWorker(path,op=op)
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
            if self.topo_2D_op.isChecked():
                self.topo_cmap_widget.setup_widget(Z)
            if self.topo_3D_op.isChecked():
                self.topo_3D_window = SurfacePlotWindowMatplot(Z)
                self.topo_3D_window.show()
        elif op == "PFM":
            Z = data
            amps = Z[0,:]
            phases = Z[1,:]
            if self.pfm_2D_amp_op.isChecked():
                self.pfm_amp_cmap_widget.setup_widget(amps)
            if self.pfm_2D_phase_op.isChecked():
                self.pfm_phase_cmap_widget.setup_widget(phases)
            if self.pfm_3D_amp_op.isChecked():
                self.pfm_3D_amp_window = SurfacePlotWindowMatplot(amps)
                self.pfm_3D_amp_window.show()
            if self.pfm_3D_phase_op.isChecked():
                self.pfm_3D_phase_window = SurfacePlotWindowMatplot(phases)
                self.pfm_3D_phase_window.show()
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