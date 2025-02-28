from PySide6.QtWidgets import(
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget
)
from PySide6.QtCore import QThreadPool
from threading import Thread
from plot_utils import calculate_grid_values
# from plot_dialog import PlotDialog
from utils import Paths
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
import matplotlib.pyplot as plt

class VisualizeTab(QWidget):
    def __init__(self):
        super().__init__()

        # WIDGETS
        self.path_input = QLineEdit()
        choose_path_btn = QPushButton("Select Data")
        self.canvas_widget = gl.GLViewWidget()
        # self.canvas_widget.setBackgroundColor("#edecec")
        self.canvas_widget.setBackgroundColor("black")

        # CONFIG
        self.path_input.setEnabled(False)

        # SIGNALS
        choose_path_btn.clicked.connect(self.get_pathname)

        # LAYOUT
        layout = QVBoxLayout()
        x_layout1 = QHBoxLayout()
        x_layout1.addWidget(QLabel("Filename:"))
        x_layout1.addWidget(self.path_input)
        x_layout1.addWidget(choose_path_btn)
        layout.addLayout(x_layout1)
        layout.addWidget(self.canvas_widget)
        self.setLayout(layout)

        # TEST
        test_y_value_input = QSpinBox()
        layout.addWidget(test_y_value_input)
        test_y_value_input.setRange(0,63)
        test_y_value_input.valueChanged.connect(self.test_create_profile_plot)
        self.z = None
        self.is_topo_plot = False
        self.test_plot = None

    def get_pathname(self):
        path_data = QFileDialog.getOpenFileName()
        path = path_data[0]
        if path:
            self.path_input.setText(path)
            plot_thread = Thread(target=self.create_plot(path))
            plot_thread.start()
    
    def create_plot(self, path):
        Z = calculate_grid_values(path,rows_to_skip=3)
        x = np.arange(Z.shape[0])
        y = np.arange(Z.shape[0])
        X,Y = np.meshgrid(x,y)
        cmap = plt.get_cmap('binary')
        minZ=np.min(Z)
        maxZ=np.max(Z)
        rgba_img = cmap((Z-minZ)/(maxZ - minZ))
        surf_plot = gl.GLSurfacePlotItem(x,y,Z, colors=rgba_img)
        self.canvas_widget.addItem(surf_plot)
        self.canvas_widget.orbit(45,90)
        self.canvas_widget.pan(dx=x.max()/2,dy=y.max()/2,dz=60)
        # TEST
        self.z = Z
        self.is_topo_plot = True

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

