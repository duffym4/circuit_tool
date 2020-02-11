from qt import *
from schematicComponent import SchematicComponent
from dialog import InfoDialogs

class AltMenu:
    def __init__(self, window):
        self.window = window
        self.schematic = self.window.schematic

        self.fileMenu = window.menuBar().addMenu("&File")
        self.componentMenu = window.menuBar().addMenu("&Component")
        self.helpMenu = window.menuBar().addMenu("&Help")

        self.close = QAction("&Close")
        self.close.triggered.connect(window.close)
        self.fileMenu.addAction(self.close)

        self.components = []
        for v in SchematicComponent.lookup:
            component = SchematicComponent.lookup[v]
            self.components.append(QAction("&" + component.name))
            self.components[-1].triggered.connect(self.changeMode(["component", v]))
            self.componentMenu.addAction(self.components[-1])

        self.aboutAction = QAction("&About")
        self.helpMenu.addAction(self.aboutAction)
        self.aboutAction.triggered.connect(lambda: InfoDialogs.about(self.window))

        self.debugAction = QAction("&Toggle Debug")
        self.helpMenu.addAction(self.debugAction)
        self.debugAction.triggered.connect(self.toggleDebug)

    def toggleDebug(self):
        self.schematic.debug = not self.schematic.debug

    def changeMode(self, mode):
        return lambda: self.schematic.changeMode(*mode)
