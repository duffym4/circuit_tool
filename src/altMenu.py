from qt import *
from schematicComponent import SchematicComponent

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
        self.aboutAction.triggered.connect(self.showAboutDialog)

        self.debugAction = QAction("&Toggle Debug")
        self.helpMenu.addAction(self.debugAction)
        self.debugAction.triggered.connect(self.toggleDebug)

    def toggleDebug(self):
        self.schematic.debug = not self.schematic.debug

    def changeMode(self, mode):
        return lambda: self.schematic.changeMode(*mode)

    def showAboutDialog(self):
        text = "<center>" \
               "<h1>Circuit Editor</h1>" \
               "&#8291;" \
               "<p>Version 0.1</p>" \
               "</center>"
        QMessageBox.about(self.window, "About Circuit Editor", text)