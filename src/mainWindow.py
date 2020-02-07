from qt import *
from schematicEditor import SchematicEditor
from altMenu import AltMenu

class MainWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.app = parent
        self.schematic = SchematicEditor(self)
        self.menu = AltMenu(self)
        self.schematic.setFocusPolicy(Qt.StrongFocus)
        self.setCentralWidget(self.schematic)

    def closeEvent(self, e):
        pass