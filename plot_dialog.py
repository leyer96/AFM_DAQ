from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout
)
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np

class PlotDialog(QDialog):
    def __init__(self,type="2d"):
        super().__init__()
        layout = QVBoxLayout()
        if type == "2d":
            self.plot_widget = pg.PlotWidget()
        elif type == "3d":
            self.plot_widget = gl.GLViewWidget()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)