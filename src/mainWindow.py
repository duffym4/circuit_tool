from qt import *
from schematicEditor import SchematicEditor
from altMenu import AltMenu
from dialog import *
from plotViewer import PlotCanvas

class MainWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.app = parent
        self.schematic = SchematicEditor(self)
        self.menu = AltMenu(self)
        self.schematic.setFocusPolicy(Qt.StrongFocus)
        self.plot = PlotCanvas(self)

        self.mainLayout = QHBoxLayout()
        self.mainLayout.addWidget(self.schematic, 60)
        self.mainLayout.addWidget(self.plot, 40)
        self.plot.hide()
        self.mainWidget = QWidget()
        self.mainWidget.setLayout(self.mainLayout)

        self.setCentralWidget(self.mainWidget)
        self.setGeometry(100, 100, 1000, 700)

    def closeEvent(self, e):
        pass

    def quit(self):
        if InfoDialogs.changesLost(self):
            self.close()

    def toggleDebug(self):
        self.schematic.debug = not self.schematic.debug
