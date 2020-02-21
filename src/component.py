from qt import *
from measure import Measure
import random, math

class Connection():

    def __init__(self, component, node):
        self.component = component
        self.node = node


class Component():

    measure, unit = "", ""

    def __init__(self, parent, value = 1):
        self.value = Measure(value, self.unit)
        self.schematicComponent = parent
        self.schematic = parent.schematic
        self.solver = self.schematic.solver
        self.name = self.schematic.getNextName(self.namePrefix)
        self.nodes = [None, None]

    def getSolveData(self):
        if self.solver.solved:
            out = self.name + " (" + self.schematicComponent.type  + ")\n"
            out += "Voltage: " + self.getSolveValue("V", "V").str() + "\n"
            out += "Current: " + self.getSolveValue("I", "A").str()
            return out
        else:
            return ""

    def getSolveValue(self, value, unit):
        return Measure(self.solver.getValue(self.name, value), unit)

    def getValueString(self):
        return self.value.lcapyStr()

    def getSolverString(self):
        contents = [self.name, *self.getSignedNodes(), self.getValueString()]
        return " ".join([str(x) for x in contents])

    def getSignedNodes(self):
        signs = {1: [*self.nodes], -1: [*self.nodes]}
        signs[1].reverse()
        return signs[self.schematicComponent.sign]


""" -------------------------------------
    Wire
    ------------------------------------- """

class Wire(Component):

    def __init__(self, parent):
        super().__init__(parent)


""" -------------------------------------
    Voltage Source
    ------------------------------------- """

class VoltageSource(Component):

    measure = "Voltage"
    unit = "V"
    namePrefix = "V"


""" -------------------------------------
    Current Source
    ------------------------------------- """

class CurrentSource(Component):

    measure = "Current"
    unit = "A"
    namePrefix = "I"


""" -------------------------------------
    Resistor
    ------------------------------------- """

class Resistor(Component):

    measure = "Resistance"
    unit = "Ω"
    namePrefix = "R"

    def getSignedNodes(self):
        return [*self.nodes]


""" -------------------------------------
    Component Lookup
    ------------------------------------- """

Component.lookup = {
    "resistor": Resistor,
    "voltageSource": VoltageSource,
    "currentSource": CurrentSource
}
