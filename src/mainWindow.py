from qt import *
from schematicEditor import SchematicEditor
from altMenu import AltMenu
from dialog import *

class MainWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.app = parent
        self.schematic = SchematicEditor(self)
        self.menu = AltMenu(self)
        self.schematic.setFocusPolicy(Qt.StrongFocus)
        self.setCentralWidget(self.schematic)
        self.setGeometry(100, 100, 1000, 700)

    def closeEvent(self, e):
        pass

    def quit(self):
        if InfoDialogs.changesLost(self):
            self.close()

    def toggleDebug(self):
        self.schematic.debug = not self.schematic.debug
