from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget
import pyqtgraph as pg
from PySide6.QtCore import Signal
import pyqtgraph.opengl as gl
import numpy as np
from scipy.signal import detrend
import matplotlib.cm as cm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class ScatterPlotWidget(pg.PlotWidget):
    def __init__(self,title="",xlabel="",ylabel="",xunits=None,yunits=None):
        super().__init__()
        self.setFixedSize(250,250)
        self.plot_item = self.plot()  
        self.plot_item.setData([], [])
        self.setTitle(title)
        self.setLabel("left", ylabel,units=yunits)
        self.setLabel("bottom", xlabel,units=xunits)

    def update_plot(self,x,y):
        self.plot_item.clear()
        self.plot_item.setData(x,y)

    def add_extra_plot(self):
        p2 =  self.plot()
        return p2
    
    def set_xlabel(self,xlabel):
        self.setLabel("bottom", xlabel)

    def set_ylabel(self,ylabel):
        self.setLabel("left", ylabel)

class CmapWidget(pg.ImageView):
    h_values = Signal(list)
    v_values = Signal(list)
    def __init__(self):
        super().__init__()
        self.setFixedSize(250,250)
        self.image_item = pg.ImageItem()
        self.prev_img = None
        self.h_line = pg.InfiniteLine(movable=True,angle=0)
        self.v_line = pg.InfiniteLine(movable=True,angle=90)
        self.ui.menuBtn.hide()
        self.ui.roiBtn.hide()
        self.ui.histogram.hide()

        self.h_line.sigPositionChangeFinished.connect(self.handle_h_line_change)
        self.v_line.sigPositionChangeFinished.connect(self.handle_v_line_change)
    
    def setup_widget(self,img,color="YlOrBr_r"):
        self.image = img
        self.n_dim = img.ndim
        if self.n_dim == 2:
            self.image_item.setImage(self.image)
        else:
            self.image = img[:,:,0]
            self.data_cube = img
            self.image_item.setImage(self.image)
        color_map = pg.colormap.getFromMatplotlib(color) 
        color_map.map(img, mode='float') 
        self.image_item.setColorMap(color_map)
        self.h_line.setBounds([0,img.shape[1]])
        self.v_line.setBounds([0,img.shape[0]])
        self.view.addItem(self.image_item)
        self.view.addItem(self.h_line)
        self.view.addItem(self.v_line)

    def handle_h_line_change(self, pos):
        pos = int(self.h_line.value())
        print(f"HORIZONTAL PIXEL {pos}")
        if self.n_dim == 2:
            values = self.image[:,pos]
        else:
            print(f"DATA CUBE SHAPE: {self.data_cube.shape}")
            y_pos = int(self.v_line.value())
            values = self.data_cube[pos,y_pos,1:]
        self.h_values.emit(values)

    def handle_v_line_change(self, pos):
        pos = int(self.v_line.value())
        print(f"VERTICAL PIXEL {pos}")  
        if self.n_dim == 2:
            values = self.image[pos,:]
        else:
            print(f"DATA CUBE SHAPE: {self.data_cube.shape}")
            x_pos = int(self.v_line.value())
            values = self.data_cube[x_pos,pos,1:]
        self.v_values.emit(values)

    def detrend_image(self):
        self.prev_img = self.image.copy()
        image = detrend(self.image)
        self.setup_widget(image)

    def go_back(self):
        if self.prev_img is not None:
            image = self.prev_img.copy()
            self.prev_img = self.image.copy()
            self.setup_widget(image)

    def set_sensitivity_rate(self,sensitivity_rate):
        image = self.image * sensitivity_rate
        self.setup_widget(image)

class SurfacePlotWindowMatplot(QWidget):
    def __init__(self, Z,title="",xlabel="",ylabel="",zlabel=""):
        super().__init__()
        self.setMinimumSize(500,500)
        self.setWindowTitle(title)
        self.fig = Figure(figsize=(5,3))
        self.fig_canvas = FigureCanvas(self.fig)
        self.fig_canvas.setParent(self)
        self.Z = Z
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.zlabel = zlabel
        self.prev_img = None
        layout = QVBoxLayout()
        layout.addWidget(NavigationToolbar(self.fig_canvas, self))
        layout.addWidget(self.fig_canvas)
        self.setLayout(layout)

        self.setup_widget()

    def setup_widget(self):
        self.fig.clear()
        ax = self.fig_canvas.figure.add_subplot(111,projection="3d")
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        ax.set_zlabel(self.zlabel)
        X = np.arange(self.Z.shape[0])
        Y = np.arange(self.Z.shape[1])
        self.X, self.Y = np.meshgrid(X, Y)
        if self.Z.ndim == 3:
            self.Z = self.Z[:,:,0]
        self.surf = ax.plot_surface(self.X,self.Y,self.Z,cmap=cm.YlOrBr)
        cbar_ax = self.fig.add_axes([0.25, 0.88, 0.5, 0.04])
        self.fig.colorbar(self.surf, cax=cbar_ax, orientation='horizontal')
        self.fig_canvas.draw()

    def detrend_image(self):
        self.prev_img = self.Z.copy()
        self.Z = detrend(self.Z)
        self.setup_widget()

    def go_back(self):
        if self.prev_img is not None:
            Z = self.prev_img.copy()
            self.prev_img = self.Z.copy()
            self.Z = Z
            self.surf.remove()
            self.setup_widget()

    def set_sensitivity_rate(self,sensitivity_rate):
        self.Z = self.Z * sensitivity_rate
        self.zlabel = "Height (nm)"
        self.setup_widget()


