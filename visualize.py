from PySide6.QtWidgets import(
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget
)
from PySide6.QtCore import QThreadPool
from threading import Thread
from plot_utils import calculate_grid_values
# from plot_dialog import PlotDialog
from plot_widgets import CmapWidget, ProfileLineWidget
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np

class VisualizeTab(QWidget):
    def __init__(self):
        super().__init__()

        # WIDGETS
        self.plot_op = QComboBox()
        self.path_input = QLineEdit()
        choose_path_btn = QPushButton("Select Data")
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
        self.pfm_2D_phase_op = QCheckBox("PFM 3D Amp")
        self.pfm_3D_amp_op = QCheckBox("PFM 2D Phase")
        self.pfm_3D_phase_op = QCheckBox("PFM 3D Phase")
        self.pfm_amp_profile_line_op = QCheckBox("PFM Amp Profile")
        self.pfm_phase_profile_line_op = QCheckBox("PFM Phase Profile")
        self.pfm_options_btns = [
            self.pfm_2D_amp_op,
            self.pfm_2D_phase_op,
            self.pfm_3D_amp_op,
            self.pfm_3D_phase_op,
            self.pfm_amp_profile_line_op,
            self.pfm_phase_profile_line_op
        ]
        # PLOT WIDGETS
        self.topo_cmap_widget = CmapWidget()
        self.amp_cmap_widget = CmapWidget()
        self.phase_cmap_widget = CmapWidget()
        self.topo_x_profile_widget = ProfileLineWidget(title="X Profile")
        self.topo_y_profile_widget = ProfileLineWidget(title="Y Profile")
        self.scatter3_widget = pg.PlotWidget()
        # CONFIG
        self.plot_op.addItems(["Topography", "PFM"])
        self.path_input.setEnabled(False)
        self.topo_2D_op.setChecked(True)
        self.topo_profile_line_op.setChecked(True)
        self.topo_3D_op.setChecked(True)
        self.amp_cmap_widget.hide()
        self.phase_cmap_widget.hide()
        self.scatter3_widget.hide()
        self.scatter3_widget.setFixedSize(200,200)
        for btn in self.pfm_options_btns:
            btn.hide()

        self.topo_cmap_widget.h_values.connect(lambda values: self.topo_x_profile_widget.update_plot(np.arange(len(values)),values))
        self.topo_cmap_widget.v_values.connect(lambda values: self.topo_y_profile_widget.update_plot(np.arange(len(values)),values))
        
        # SIGNALS
        choose_path_btn.clicked.connect(self.get_pathname)
        self.plot_op.currentIndexChanged.connect(self.handle_study_option_change)

        # LAYOUT
        layout = QVBoxLayout()

        x_layout1 = QHBoxLayout()
        x_layout1.addWidget(QLabel("Study:"))
        x_layout1.addWidget(self.plot_op)

        x_layout2 = QHBoxLayout()
        x_layout2a = QHBoxLayout()
        x_layout2b = QHBoxLayout()
        x_layout2.addWidget(self.topo_2D_op)
        x_layout2.addWidget(self.topo_3D_op)
        x_layout2.addWidget(self.topo_profile_line_op)
        x_layout2a.addWidget(self.pfm_2D_amp_op)
        x_layout2a.addWidget(self.pfm_2D_phase_op)
        x_layout2a.addWidget(self.pfm_3D_amp_op)
        x_layout2b.addWidget(self.pfm_3D_phase_op)
        x_layout2b.addWidget(self.pfm_amp_profile_line_op)
        x_layout2b.addWidget(self.pfm_phase_profile_line_op)

        x_layout3 = QHBoxLayout()
        x_layout3.addWidget(QLabel("Filename:"))
        x_layout3.addWidget(self.path_input)
        x_layout3.addWidget(choose_path_btn)

        x_layout4 = QHBoxLayout()
        x_layout4.addWidget(self.topo_cmap_widget)
        x_layout4.addWidget(self.amp_cmap_widget)
        x_layout4.addWidget(self.phase_cmap_widget)
        
        x_layout5 = QHBoxLayout()
        x_layout5.addWidget(self.topo_x_profile_widget)
        x_layout5.addWidget(self.topo_y_profile_widget)
        x_layout5.addWidget(self.scatter3_widget)

        layout.addLayout(x_layout1)
        layout.addLayout(x_layout2)
        layout.addLayout(x_layout2a)
        layout.addLayout(x_layout2b)
        layout.addLayout(x_layout3)
        layout.addLayout(x_layout4)
        layout.addLayout(x_layout5)
        self.setLayout(layout)
        

    def handle_study_option_change(self, index):
        if index == 0:
            for btn in self.pfm_options_btns:
                btn.hide()
                btn.setChecked(False)
        else:
            for btn in self.pfm_options_btns:
                btn.show()
    
    def get_pathname(self):
        path_data = QFileDialog.getOpenFileName()
        path = path_data[0]
        if path:
            self.path_input.setText(path)
            plot_thread = Thread(target=self.create_plot,args=(path,))
            plot_thread.start()
    
    def create_plot(self, path):
        op = self.plot_op.currentIndex()
        Z = calculate_grid_values(path,op=op,rows_to_skip=3)
        self.topo_cmap_widget.setup_widget(Z)
        if op == 1:
            self.test_plot = self.plot_widget.addPlot(row=0,col=1)
            self.test_plot1 = self.plot_widget.addPlot(row=1,col=0)
            self.test_plot2 = self.plot_widget.addPlot(row=1,col=1)
            x = np.arange(10)
            y = x
            self.test_plot1.plot(x=x,y=y,pen="r")
            y = x**2
            self.test_plot2.plot(x=x,y=y,pen="b")


    def test_create_profile_plot(self, y_val):
        if not self.is_topo_plot:
            return
        if self.test_plot != None:
            self.test_plot.close()
        y = self.z[y_val,:]
        x = np.arange(y.size)
        m,b = np.polyfit(x,y,1)
        print(f"m = {m} AND b = {b}")
        self.test_plot = pg.GraphicsLayoutWidget()
        self.test_plot.addPlot(x=x,y=y,row=0,col=0)
        self.test_plot.addPlot(x=x,y=y-(x*m),row=1,col=0,pen="r")
        self.test_plot.show()

