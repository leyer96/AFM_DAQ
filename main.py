from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
)
from threading import Thread
from acquire import AcquireTab
from visualize import VisualizeTab
from send import SendDataTab
from multi_freq import MultiFreqTab
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar


class DAQInterface:
    def __init__(self, main_window):
        self.main_window = main_window
        self.main_window.setWindowTitle("AFM_DAQ_Visualizer")
        self.acquire_window = AcquireTab()
        self.visualize_window = VisualizeTab()
        self.send_data_window = SendDataTab()
        self.multi_freq_window = MultiFreqTab()

        self.create_widgets()
        self.main_window.show()

    def create_widgets(self):
        tab_widget = QTabWidget()
        tab_widget.addTab(self.acquire_window, "Acquire Data")
        tab_widget.addTab(self.send_data_window, "Send Data")
        tab_widget.addTab(self.visualize_window, "Visualize")
        # tab_widget.addTab(self.multi_freq_window, "MULTI-FREQ")
        
        self.main_window.setCentralWidget(tab_widget)


if __name__ == "__main__":
    app = QApplication([])
    main_window = QMainWindow()
    interface = DAQInterface(main_window)
    # interface.main_window.showFullScreen()
    app.exec()
