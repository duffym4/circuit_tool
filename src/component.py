from qt import *
from measure import Measure
import random, math, sympy

class Connection():

    def __init__(self, component, node):
        self.component = component
        self.node = node


class Component():

    measure, unit = "", ""
    signed = True
    initial = False

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
            out = [[self.name + " (" + self.schematicComponent.type  + ")", "selected"]]
            out.append(["Voltage: ", "selected"])
            out.append([V.str(), "standard"])
            out.append(["Current: ", "selected"])
            out.append([I.str(), "standard"])
            return out
        else:
            return ""

    # Returns a measure of a value of component
    def getSolveValue(self, value, unit):
        return Measure(self.solver.getValue(self.name, value), unit)
            # Returns a measure of a value of component

    def getSolvePlots(self, time):
        if self.solver.solved:
            results = {"name": self.name}
            for x in ["V", "I"]:
                results[x] = self.solver.getValuesInDomain(self.name, x, time)
            return results
        else:
            return {"name": self.name}

    # Returns value in a form readable by lcapy
    def getValueString(self):
        return self.value.lcapyStr()

    # Return the string that adds the component to the lcapy circuit: <name> <*nodes> <value>
    def getSolverString(self):
        contents = [self.name, *self.getSignedNodes(), self.getValueString()]
        return " ".join([str(x) for x in contents])

    # Returns a copy of nodes reordered to match the sign of the component
    def getSignedNodes(self):
        if not self.signed:
            return [*self.nodes]
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
    namePrefix = "C"


""" -------------------------------------
    Resistor
    ------------------------------------- """

class Resistor(Component):

    measure = "Resistance"
    unit = "Ω"
    namePrefix = "R"
    signed = False


""" -------------------------------------
    Capacitor
    ------------------------------------- """

class Capacitor(Component):

    measure = "Capacitance"
    unit = "F"
    namePrefix = "C"
    signed = False
    initial = True

""" -------------------------------------
    Inductor
    ------------------------------------- """

class Inductor(Component):

    measure = "Inductance"
    unit = "H"
    namePrefix = "L"
    signed = False
    initial = True

""" -------------------------------------
    Component Lookup
    ------------------------------------- """

Component.lookup = {
    "resistor": Resistor,
    "voltageSource": VoltageSource,
    "currentSource": CurrentSource,
    "capacitor": Capacitor,
    "inductor": Inductor
}
