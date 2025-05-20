from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
)
from PySide6.QtGui import QAction
from acquire import AcquireTab
from visualize import VisualizeTab
from send import SendDataTab
from multi_freq import MultiFreqTab
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AFM_DAQ_Visualizer")
        #TABS
        self.acquire_tab = AcquireTab()
        self.visualize_tab = VisualizeTab()
        self.send_data_tab = SendDataTab()
        self.multi_freq_tab = MultiFreqTab()

        tab_widget = QTabWidget()
        tab_widget.addTab(self.acquire_tab, "Acquire Data")
        tab_widget.addTab(self.send_data_tab, "Send Data")
        tab_widget.addTab(self.visualize_tab, "Visualize")
        
        #MENU
        menu = self.menuBar()
        tools_menu = menu.addMenu("&Tools")
        convert_files_menu = tools_menu.addMenu("&Convert Files")

        ## ACTIONS
        to_csv_action = QAction(
            text="to .csv",
            parent=convert_files_menu)
        to_npy_action = QAction(
            text="to .npy",
            parent=convert_files_menu)
        convert_files_menu.addAction(to_csv_action)
        convert_files_menu.addAction(to_npy_action)

        to_csv_action.triggered.connect(self.convert_tdms_to_csv)
        to_npy_action.triggered.connect(self.convert_tdms_to_numpy)

        self.setCentralWidget(tab_widget)

    def convert_tdms_to_numpy(self):
        pass

    def convert_tdms_to_csv(self):
        pass


if __name__ == "__main__":
    app = QApplication([])
    w = MainWindow()
    w.show()
    # interface.main_window.showFullScreen()
    app.exec()
