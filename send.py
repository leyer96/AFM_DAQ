from PySide6.QtWidgets import(
    QLabel,
    QVBoxLayout,
    QWidget
)

class SendDataTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Send Data Window"))
        self.setLayout(layout)