import sys
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication

from .ui import MainWindow
from .storage import Storage


class BlaaahApp:
    def __init__(self):
        self.app = QApplication([])
        self.storage = Storage()
        self.window: Optional[MainWindow] = None

    def run(self):
        self.window = MainWindow(self.storage)
        self.window.show()
        sys.exit(self.app.exec())
