from PySide6.QtWidgets import(
    QComboBox,
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
from plot_utils import calculate_grid_values, calculate_grid_values_amp
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
        self.plot_op = QComboBox()
        # self.plot_widget = pg.PlotWidget()
        self.plot_widget = pg.GraphicsLayoutWidget()

        # CONFIG
        self.plot_op.addItems(["Topography", "PFM"])
        self.path_input.setEnabled(False)
        # self.plot_widget.getPlotItem().getAxis('bottom').setVisible(False)
        # self.plot_widget.getPlotItem().getAxis('left').setVisible(False)

        # SIGNALS
        choose_path_btn.clicked.connect(self.get_pathname)

        # LAYOUT
        layout = QVBoxLayout()
        x_layout1 = QHBoxLayout()
        x_layout1.addWidget(QLabel("Study:"))
        x_layout1.addWidget(self.plot_op)
        x_layout2 = QHBoxLayout()
        x_layout2.addWidget(QLabel("Filename:"))
        x_layout2.addWidget(self.path_input)
        x_layout2.addWidget(choose_path_btn)
        layout.addLayout(x_layout1)
        layout.addLayout(x_layout2)
        layout.addWidget(self.plot_widget)
        layout.addStretch()
        self.setLayout(layout)
        

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
        self.cm_plot = self.plot_widget.addPlot(row=0,col=0)
        cm_image_item = pg.ImageItem()
        self.cm_plot.addItem(cm_image_item)
        self.cm_plot.setAspectLocked(True)
        color_map = pg.colormap.getFromMatplotlib("pink") 
        color_map.map(Z, mode='float') 
        cm_image_item.setImage(Z)
        cm_image_item.setColorMap(color_map)
        if op == 0:
            self.profile_line = self.plot_widget.addPlot(row=0,col=1)
            x = np.arange(10)
            y = x
            self.profile_line.plot(x=x,y=y,pen="r")
        elif op == 1:
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

