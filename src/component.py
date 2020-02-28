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

    # Gets the contents of the info box for hovering a solved component
    def getSolveData(self):
        if self.solver.solved:
            V = self.getSolveValue("V", "V")
            I = self.getSolveValue("I", "A")
            V.autoPrefix()
            I.autoPrefix()
            out = self.name + " (" + self.schematicComponent.type  + ")\n"
            out += "Voltage: " + V.str() + "\n"
            out += "Current: " + I.str()
            return out
        else:
            return ""

    # Returns a measure of a value of component
    def getSolveValue(self, value, unit):
        return Measure(self.solver.getValue(self.name, value), unit)

    # Returns value in a form readable by lcapy
    def getValueString(self):
        return self.value.lcapyStr()

    # Return the string that adds the component to the lcapy circuit: <name> <*nodes> <value>
    def getSolverString(self):
        contents = [self.name, *self.getSignedNodes(), self.getValueString()]
        return " ".join([str(x) for x in contents])

    # Returns a copy of nodes reordered to match the sign of the component
    def getSignedNodes(self):
        signs = {1: [*self.nodes], -1: [*self.nodes]}
        signs[1].reverse()
        #if self.schematicComponent.horizontal:
        #    return signs[-self.schematicComponent.sign]
        #else:
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

    # Resistor direction does not matter
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
