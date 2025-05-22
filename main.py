from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
    QFileDialog,
    QMainWindow,
    QTabWidget,
)
from PySide6.QtCore import QThreadPool
from PySide6.QtGui import QAction
from acquire import AcquireTab
from visualize import VisualizeTab
from send import SendDataTab
from multi_freq import MultiFreqTab
from workers import ConverterWorker


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
        image_menu = menu.addMenu("&Image")

        # ACTIONS
        ## TOOLS
        to_csv_action = QAction(
            text="to .csv",
            parent=convert_files_menu)
        to_npy_action = QAction(
            text="to .npy",
            parent=convert_files_menu)
        convert_files_menu.addAction(to_csv_action)
        convert_files_menu.addAction(to_npy_action)

        to_csv_action.triggered.connect(lambda: self.convert_tdms("csv"))
        to_npy_action.triggered.connect(lambda: self.convert_tdms("npy"))
        ## IMAGE
        detrend_image_action = QAction(
            text="Detrend image",
            parent=image_menu)
        go_back_image_action = QAction(
            text="Go Back",
            parent=image_menu)
        convert_V_to_nm = QAction(
            text="Convert to nm",
            parent=image_menu)
        image_menu.addAction(detrend_image_action)
        image_menu.addAction(go_back_image_action)
        image_menu.addAction(convert_V_to_nm)

        detrend_image_action.triggered.connect(self.visualize_tab.detrend_data)
        go_back_image_action.triggered.connect(self.visualize_tab.go_back)
        convert_V_to_nm.triggered.connect(self.visualize_tab.add_sensitivity_rate)

        # THREADPOOL
        self.threadpool = QThreadPool()

        self.setCentralWidget(tab_widget)

    def convert_tdms(self, mode="csv"):
        file,_ = QFileDialog.getOpenFileName(self,caption="Select File to Convert")
        if file:
            target = QFileDialog.getExistingDirectory(self, caption="Select Target Folder")
            if target:
                worker = ConverterWorker(file,target,mode=mode)
                self.threadpool.start(worker)
                dlg = QMessageBox.information(self,"Status", "Converting... (you can close this dialog)")
                worker.signals.finished.connect(lambda: QMessageBox.information(self,"Status", "Succesfully converted file"))
                worker.signals.error.connect(lambda: QMessageBox.warning(self,"Status", "Error while converted file"))


if __name__ == "__main__":
    app = QApplication([])
    w = MainWindow()
    w.show()
    # interface.main_window.showFullScreen()
    app.exec()
