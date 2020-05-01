from component import *
import random, math, lcapy, sympy

class Solver():

    def __init__(self, parent):
        self.schematic = parent
        self.node = 0
        self.components = []
        self.wires = {}
        self.circuit = lcapy.Circuit()
        self.solved = False

    def solve(self, components):
        self.solved = True
        try:
            self.circuit = lcapy.Circuit()
            for c in self.components:
                print(c.component.getSolverString())
                self.circuit.add(c.component.getSolverString())
            gnd = self.circuit[components[0].component.name].V
        except Exception as e:
            self.solved = False
            return e
        return None

    def getValue(self, name, value):
        domain = lcapy.t
        if self.schematic.domain == "s":
            domain = lcapy.s
        if self.solved:
            return getattr(self.circuit[name], value)(domain)
        else:
            return ""

    def getValuesInDomain(self, name, value, t):
        if self.solved:
            return getattr(self.circuit[name], value)(lcapy.t).evaluate(t)
        else:
            return [0]

    def nextNode(self):
        self.node += 1
        return self.node

    def reloadSchematic(self):
        print("solving...")
        wires, components, grounds = self.componentsByType()
        self.wires = {}
        self.resetNodes(components)
        self.node = 0
        for c in components:
            component = c.component
            myNodes = c.adjacentComponents(components)
            myGrounds = c.adjacentComponents(grounds)
            for i in range(len(myNodes)):
                # If node hasn't already been calculated
                if not component.nodes[i]:
                    # If any attached grounds, node name is 0
                    node = 0
                    if len(myGrounds[i]) == 0:
                        node = self.nextNode()
                    component.nodes[i] = node
                    # Set node name of all attached nodes to match
                    for x in myNodes[i]:
                        x.component.component.nodes[x.node] = node
        self.components = components
        self.connectWires(wires, components, grounds)
        return self.solve(components)

    def connectWires(self, wires, components, grounds):
        for wire in wires:
            minNode = [self.nextNode()]
            attached = []
            self.nodesOnWire(wire, wires, components, grounds, minNode, attached, [wire])
            self.wires[wire] = minNode[0]
            for x in attached:
                x.component.component.nodes[x.node] = minNode[0]

    def nodesOnWire(self, wire, wires, components, grounds, minNode, attached, visited):
        myNodes = wire.adjacentComponents(components)
        myWires = wire.adjacentComponents(wires)
        myGrounds = wire.adjacentComponents(grounds)
        for g in myGrounds:
            if len(g) > 0:
                minNode[0] = 0
        for node in myNodes:
            for x in node:
                attached.append(x)
                minNode[0] = min(minNode[0], x.component.component.nodes[x.node])
        for node in myWires:
            for w in node:
                if not w.component in visited:
                    visited.append(w.component)
                    self.nodesOnWire(w.component, wires, components, grounds, minNode, attached, visited)

    def componentsByType(self):
        wires, components, grounds = [], [], []
        for c in self.schematic.components:
            if c.wire:
                wires.append(c)
            elif c.ground:
                grounds.append(c)
            else:
                components.append(c)
        return wires, components, grounds

    def resetNodes(self, components):
        for c in components:
            for i in range(len(c.component.nodes)):
                c.component.nodes[i] = None
