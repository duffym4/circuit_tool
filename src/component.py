from qt import *
import random, math

class Component():

    unitPrefixes = {
        "m": -3,
        "": 0,
        "k": 3,
        "M": 6
    }

    def __init__(self, parent, value):
        self.value = value
        self.unitPrefix = ""
        self.schematicComponent = parent

""" -------------------------------------
    Voltage Source
    ------------------------------------- """

class VoltageSource(Component):

    type = "Voltage Source"
    measure = "Voltage"
    unit = "V"
    namePrefix = "V"


""" -------------------------------------
    Current Source
    ------------------------------------- """

class CurrentSource(Component):

    type = "Current Source"
    measure = "Current"
    unit = "A"
    namePrefix = "I"


""" -------------------------------------
    Resistor
    ------------------------------------- """

class Resistor(Component):

    type = "Resistor"
    measure = "Resistance"
    unit = "Ω"
    namePrefix = "R"


""" -------------------------------------
    Component Lookup
    ------------------------------------- """

Component.lookup = {
    "resistor": Resistor,
    "voltageSource": VoltageSource,
    "currentSource": CurrentSource
}
