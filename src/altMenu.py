from qt import *
from schematicComponent import SchematicComponent
from dialog import InfoDialogs, CircuitProperties
from schematicEditor import SchematicEditor

class AltMenu:
    def __init__(self, window):
        self.window = window
        self.schematic = self.window.schematic

        self.menu = {
            "File": {
                "New":  self.window.schematic.new,
                "Save": self.window.schematic.save,
                "Load": self.window.schematic.load,
                "Quit": self.window.quit
            },
            "Circuit": {
                "Inspect": self.window.schematic.solve,
                "Configure": lambda: CircuitProperties(self.window)
            },
            "Component": {}, # Populated Programmatically
            "Help": {
                "About": lambda: InfoDialogs.about(self.window),
                "Debug": self.window.toggleDebug
            }
        }

        self.menus = {}
        self.actions = []

        for submenu in self.menu:
            self.menus[submenu] = window.menuBar().addMenu("&" + submenu)
            for action in self.menu[submenu]:
                qa = QAction("&" + action)
                qa.triggered.connect(self.menu[submenu][action])
                self.menus[submenu].addAction(qa)
                self.actions.append(qa)

        for v in SchematicComponent.lookup:
            component = SchematicComponent.lookup[v]
            qa = QAction("&" + component.type)
            qa.triggered.connect(self.changeMode(["component", v]))
            self.menus["Component"].addAction(qa)
            self.actions.append(qa)

    def changeMode(self, mode):
        return lambda: self.schematic.changeMode(*mode)
