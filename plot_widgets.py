from PySide6.QtWidgets import QDialog, QVBoxLayout
import pyqtgraph as pg
from PySide6.QtCore import Signal
import pyqtgraph.opengl as gl
import numpy as np
import matplotlib.cm as cm

class ScatterPlotWidget(pg.PlotWidget):
    def __init__(self,title="",xlabel="",ylabel=""):
        super().__init__()
        self.setFixedSize(300,300)
        self.plot_item = self.plot()  
        self.plot_item.setData([], [])
        self.setTitle(title)
        self.setLabel("left", xlabel)
        self.setLabel("bottom", ylabel)

    def update_plot(self,x,y):
        self.plot_item.clear()
        self.plot_item.setData(x,y)

class CmapWidget(pg.ImageView):
    h_values = Signal(list)
    v_values = Signal(list)
    def __init__(self):
        super().__init__()
        self.setFixedSize(300,300)
        self.image_item = pg.ImageItem()
        self.h_line = pg.InfiniteLine(movable=True,angle=0)
        self.v_line = pg.InfiniteLine(movable=True,angle=90)
        self.ui.menuBtn.hide()
        self.ui.roiBtn.hide()
        self.ui.histogram.hide()

        self.h_line.sigPositionChangeFinished.connect(self.handle_h_line_change)
        self.v_line.sigPositionChangeFinished.connect(self.handle_v_line_change)
    
    def setup_widget(self,img,color="pink"):
        self.image = img
        self.n_dim = img.ndim
        if self.n_dim == 2:
            self.image_item.setImage(img)
        else:
            img = img[:,:,0]
            self.image_item.setImage(img)
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
        if self.n_dim == 2:
            values = self.image[:,pos]
        else:
            y_pos = int(self.v_line.value())
            values = self.image[pos,y_pos,1:]
        self.h_values.emit(values)

    def handle_v_line_change(self, pos):
        pos = int(self.v_line.value())
        if self.n_dim == 2:
            values = self.image[pos,:]
        else:
            x_pos = int(self.v_line.value())
            values = self.image[x_pos,pos,1:]
        self.v_values.emit(values)

class SurfacePlotDialog(QDialog):
    def __init__(self,Z,parent=None):
        super().__init__(parent)
        self.setWindowTitle("3D Surface Plot")
        self.resize(300, 300)
        
        self.gl_widget = gl.GLViewWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.gl_widget)
        self.setLayout(layout)
        
        x = np.arange(Z.shape[1])
        y = np.arange(Z.shape[0])
        Z_min, Z_max = Z.min(), Z.max()
        Z_norm = (Z - Z_min) / (Z_max - Z_min)
        cmap = cm.get_cmap("pink")
        colors = cmap(Z_norm)[:, :, :3]
        
        surface = gl.GLSurfacePlotItem(x=x,y=y,z=Z,colors=colors)
        surface.setGLOptions("opaque")
        self.gl_widget.addItem(surface)

