from PySide6.QtWidgets import (
    QWidget
    )
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor

class ConnectionStatusIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.status = 0
        self.r = 2
        self.setFixedSize(2*self.r,2*self.r) 

    def toggle_status(self):
        self.status = not self.status
        self.update() 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.status:
            color = QColor(0, 255, 0)
        else:
            color = QColor(255, 0, 0)

        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        center_x = self.width() // 2  
        center_y = self.height() // 2 
        painter.drawEllipse(center_x - self.r, center_y - self.r, self.r * 2, self.r * 2) 