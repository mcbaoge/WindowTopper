import sys
import ctypes

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

from ui import MainWindow


def main():
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("windows.topper.manager")

    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
