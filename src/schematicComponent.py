from qt import *
from component import *
from dialog import *
from util import *
import random, math

class SchematicComponent():

    """ -------------------------------------
        Initialization
        ------------------------------------- """

    type = None

    def __init__(self, parent, x, y, sign, horizontal = True):
        self.schematic = parent
        self.x, self.y = x, y
        self.horizontal = horizontal
        self.sign = sign
        self.overlapped, self.selected, self.new = False, False, False
        self.colors = self.schematic.colors
        self.wire, self.ground = False, False
        self.name = ""
        self.drawName = False

    """ -------------------------------------
        Edit Dialog
        ------------------------------------- """

    def edit(self):
        dialog = EditComponent(self.schematic.window, self.component)
        dialog.show()

    """ -------------------------------------
        Events
        ------------------------------------- """

    def draw(self, qp):
        s = self.schematic.grid_size
        self.font = QFont('SansSerif', 10*(s/20))
        qp.setFont(self.font)
        if self.schematic.debug:
            self.drawBoundingBoxes(qp)
            self.drawEndPoints(qp)
        qp.setPen(QPen(self.colors["standard"], math.floor(s/10)))
        if self.new:
            qp.setPen(QPen(self.colors["new"], math.floor(s/10)))
        elif self.overlapped:
            qp.setPen(QPen(self.colors["overlapped"], math.floor(s/10)))
        elif self.selected:
            qp.setPen(QPen(self.colors["selected"], math.floor(s/10)))
        self.drawComponent(qp)

    """ -------------------------------------
        Painting
        ------------------------------------- """

    def drawBoundingBoxes(self, qp):
        s, x0, y0, w0, h0 = self.getDrawValues()
        qp.setPen(QPen(self.colors["coreBoundingBox"], math.floor(s/10)))
        qp.drawRect(*self.getCoreBoundingBox())
        qp.setPen(QPen(self.colors["boundingBox"], math.floor(s/10)))
        qp.drawRect(*self.getBoundingBox())

    def drawEndPoints(self, qp):
        s, x0, y0, w0, h0 = self.getDrawValues()
        x0 = self.schematic.offset_x
        y0 = self.schematic.offset_y
        qp.setPen(QPen(self.colors["coreBoundingBox"], math.floor(s/10)))
        for c in self.getConnections():
            qp.drawEllipse(x0 + c[0]*s - s/4, y0 + c[1]*s - s/4, s/2, s/2)

    def drawLeads(self, qp):
        s = self.schematic.grid_size
        self.drawLine(qp, 0, 0, s*.95, 0)
        self.drawLine(qp, 3.05*s, 0, 4*s, 0)

    def getLabelBox(self):
        s, x0, y0, w0, h0 = self.getDrawValues()
        y, h = y0 + (1.25*s)*h0 - (1.5*s)*w0, s
        w = stringWidth(self.getLabelText(), self.font) + s/5
        if self.drawName:
            h = 2*s
            y -= s/2
        return QRectF(x0 - (w/2) + 2*s*w0 - 1.5*s*h0, y, w, h)

    def drawLabelBox(self, qp):
        qp.fillRect(self.getLabelBox(), self.colors["labelBox"])

    def getLabelText(self):
        lbl = self.component.value.str()
        if self.drawName:
            lbl = self.component.name + "\n" + lbl
        return lbl

    def drawLabel(self, qp):
        s, x0, y0, w0, h0 = self.getDrawValues()
        align = Qt.AlignCenter
        if h0:
            align = Qt.AlignRight | Qt.AlignCenter
        qp.setPen(QPen(self.colors["label"], math.floor(s/10)))
        qp.drawText(self.getLabelBox(), align, self.getLabelText())

    def drawRoundSchematicComponent(self, qp):
        s = self.schematic.grid_size
        self.drawLeads(qp)
        self.drawEllipse(qp, s, -s, 2*s, 2*s)

    def drawRect(self, qp, x, y, w, h):
        s, x0, y0, w0, h0 = self.getDrawValues()
        qp.drawRect(x0 + x*w0 + y*h0,
                    y0 + y*w0 + x*h0,
                    w*w0 + h*h0,
                    h*w0 + w*h0)

    def drawLine(self, qp, x1, y1, x2, y2):
        s, x0, y0, w0, h0 = self.getDrawValues()
        x, y, w, h = self.getBoundingBox()
        if self.sign == -1:
            x0 += w*w0
            y0 += h*h0
        qp.drawLine(x0 + x1*self.sign*w0 + y1*self.sign*h0,
                    y0 + y1*self.sign*w0 + x1*self.sign*h0,
                    x0 + x2*self.sign*w0 + y2*self.sign*h0,
                    y0 + y2*self.sign*w0 + x2*self.sign*h0)

    def drawEllipse(self, qp, x, y, w, h):
        s, x0, y0, w0, h0 = self.getDrawValues()
        qp.drawEllipse(x0 + x*w0 + y*h0,
                       y0 + y*w0 + x*h0,
                       w*w0 + h*h0,
                       h*w0 + w*h0)

    def drawArc(self, qp, x, y, w, h, start, length):
       s, x0, y0, w0, h0 = self.getDrawValues()
       qp.drawArc(x0 + x*w0 + y*h0,
                  y0 + y*w0 + x*h0,
                  w*w0 + h*h0,
                  h*w0 + w*h0,
                  (start + 90*h0) * 16, length * 16)

    """ -------------------------------------
        Coordinate Calculations
        ------------------------------------- """

    def getCoreBoundingBox(self):
        s, x0, y0, w0, h0 = self.getDrawValues()
        return x0 - s*h0*0.8 + s*w0*1.2, y0 - s*w0*0.8 + s*h0*1.2, 1.6*s, 1.6*s

    def getBoundingBox(self):
        s, x0, y0, w0, h0 = self.getDrawValues()
        return x0 - s*h0, y0 - s*w0, 2*s + 2*s*w0, 2*s + 2*s*h0

    def overlapping(self, component):
        x1, y1, w1, h1 = self.getCoreBoundingBox()
        x2, y2, w2, h2 = self.getBoundingBox()
        x3, y3, w3, h3 = component.getCoreBoundingBox()
        x4, y4, w4, h4 = component.getBoundingBox()
        if x1 + w1 > x4 and x1 < x4 + w4 and y1 + h1 > y4 and y1 < y4 + h4:
            return True
        if x2 + w2 > x3 and x2 < x3 + w3 and y2 + h2 > y3 and y2 < y3 + h3:
            return True

    def selecting(self, x, y):
        x1, y1, w1, h1 = self.getBoundingBox()
        if x > x1 and x < x1 + w1 and y > y1 and y < y1 + h1:
            return True

    def position(self, x, y):
        x0, y0, w, h = self.getBoundingBox()
        w0, h0 = int(self.horizontal), int(not self.horizontal)
        self.x = math.floor((x - self.schematic.offset_x - w0*(w/2))/self.schematic.grid_size + .5)
        self.y = math.floor((y - self.schematic.offset_y - h0*(h/2))/self.schematic.grid_size + .5)

    def getDrawValues(self):
        s = self.schematic.grid_size
        x0 = self.x*s + self.schematic.offset_x
        y0 = self.y*s + self.schematic.offset_y
        w0, h0 = int(self.horizontal), int(not self.horizontal)
        return s, x0, y0, w0, h0

    def rotate(self):
        self.horizontal = not self.horizontal
        if self.horizontal:
            self.sign *= -1

    """ -------------------------------------
        Solver Methods
        ------------------------------------- """

    def getSolveData(self):
        if hasattr(self, "component"):
            return self.component.getSolveData()

    def getSolvePlots(self, time):
        if hasattr(self, "component"):
            return self.component.getSolvePlots(time)

    def adjacentComponents(self, components):
        nodes = self.getConnections()
        connections = []
        for node in nodes:
            connections.append([])
            for component in components:
                if component != self:
                    otherConnections = component.getConnections()
                    if node in otherConnections:
                        c = Connection(component, otherConnections.index(node))
                        connections[-1].append(c)
        return connections

    def getConnections(self):
        s, x0, y0, w0, h0 = self.getDrawValues()
        return [(self.x, self.y), (self.x + 4*w0, self.y + 4*h0)]

    """ -------------------------------------
        Saving/Loading Methods
        ------------------------------------- """

    def serialize(self):
        data = {
            "type": type(self),
            "x": self.x,
            "y": self.y,
            "sign": self.sign,
            "horizontal": self.horizontal,
            "drawName": self.drawName,
        }
        if hasattr(self, "component"):
            componentData = {
                "value": self.component.value.value,
                "unitPrefix": self.component.value.unitPrefix,
                "name": self.component.name,
            }
            data = {**data, **componentData}
        if self.wire:
            data["length"] = self.length
        return data

    def deserialize(self, data):
        self.x = data["x"]
        self.y = data["y"]
        self.sign = data["sign"]
        self.horizontal = data["horizontal"]
        self.drawName = data["drawName"]
        if hasattr(self, "component"):
            self.component.value.value = data["value"]
            self.component.value.unitPrefix = data["unitPrefix"]
            self.component.name = data["name"]
        if self.wire:
            self.length = data["length"]

""" -------------------------------------
    Wires
    ------------------------------------- """

class SchematicWire(SchematicComponent):

    type = "Wire"

    def __init__(self, parent, x, y, sign, horizontal):
        super().__init__(parent, x, y, sign, horizontal)
        self.length = 0
        self.wire = True

    def drawComponent(self, qp):
        s, x0, y0, w0, h0 = self.getDrawValues()
        l = s*self.length*self.sign
        qp.drawLine(x0, y0, x0 + l*w0, y0 + l*h0)

    def edit(self):
        pass

    def drawLabel(self, qp):
        pass

    def drawLabelBox(self, qp):
        pass

    def getSolveData(self):
        solver = self.schematic.solver
        measure = Measure(solver.getValue(solver.wires[self], "V"), "V")
        measure.autoPrefix()
        return [["Wire", "selected"], [measure.str(), "standard"]]

    def getSolvePlots(self, time):
        solver = self.schematic.solver
        v = solver.getValuesInDomain(solver.wires[self], "V", time)
        return {"name": "Wire", "V": v}

    def positive(self):
        if self.sign == -1:
            s, x0, y0, w0, h0 = self.getDrawValues()
            self.x -= self.length*w0
            self.y -= self.length*h0
            self.sign = 1

    def getCoreBoundingBox(self):
        return 0, 0, 0, 0

    def getBoundingBox(self):
        s, x0, y0, w0, h0 = self.getDrawValues()
        l = s*self.length
        b = l*mp2oz(self.sign)
        return x0 - .1*s - w0*b, y0 - .1*s - h0*b, .2*s + w0*l, .2*s + h0*l

    def resizeWire(self, x, y):
        x0 = math.floor((x - self.schematic.offset_x)/self.schematic.grid_size + .5)
        y0 = math.floor((y - self.schematic.offset_y)/self.schematic.grid_size + .5)
        dx, dy = abs(x0 - self.x), abs(y0 - self.y)
        self.length = max(dx, dy)
        self.horizontal = dx > dy
        self.sign = self.horizontal * (x0 > self.x)
        self.sign += (not self.horizontal) * (y0 > self.y)
        self.sign = self.sign*2 - 1

    def rotate(self):
        pass

    def getConnections(self):
        s, x0, y0, w0, h0 = self.getDrawValues()
        connections = []
        for i in range(self.length + 1):
            connections.append((int(self.x + i*w0), int(self.y + i*h0)))
        return connections

""" -------------------------------------
    Voltage Source
    ------------------------------------- """

class SchematicVoltageSource(SchematicComponent):

    type = "Voltage Source"

    def __init__(self, parent, x, y, sign, horizontal = True):
        super().__init__(parent, x, y, sign, horizontal)
        self.component = VoltageSource(self)

    def drawComponent(self, qp):
        s = self.schematic.grid_size
        self.drawRoundSchematicComponent(qp)
        self.drawLine(qp, s*1.3, 0, s*1.7, 0)
        self.drawLine(qp, s*2.7, 0, s*2.3, 0)
        self.drawLine(qp, s*2.5, -s*.2, s*2.5, s*.2)

""" -------------------------------------
    Current Source
    ------------------------------------- """

class SchematicCurrentSource(SchematicComponent):

    type = "Current Source"

    def __init__(self, parent, x, y, sign, horizontal = True):
        super().__init__(parent, x, y, sign, horizontal)
        self.component = CurrentSource(self)

    def drawComponent(self, qp):
        s = self.schematic.grid_size
        self.drawRoundSchematicComponent(qp)
        self.drawLine(qp, s*1.3, 0, s*2.7, 0)
        self.drawLine(qp, s*2.7, 0, s*2.5, s*.2)
        self.drawLine(qp, s*2.7, 0, s*2.5, -s*.2)

""" -------------------------------------
    Resistor
    ------------------------------------- """

class SchematicResistor(SchematicComponent):

    type = "Resistor"

    def __init__(self, parent, x, y, sign, horizontal = True):
        super().__init__(parent, x, y, sign, horizontal)
        self.component = Resistor(self)

    def drawComponent(self, qp):
        s = self.schematic.grid_size
        self.drawLeads(qp)
        self.drawLine(qp, s, 0, 1.4*s, -2*s/3)
        self.drawLine(qp, 1.4*s, -2*s/3, 1.8*s, 2*s/3)
        self.drawLine(qp, 1.8*s, 2*s/3, 2.2*s, -2*s/3)
        self.drawLine(qp, 2.2*s, -2*s/3, 2.6*s, 2*s/3)
        self.drawLine(qp, 2.6*s, 2*s/3, 3*s, 0)

""" -------------------------------------
    Capacitor
    ------------------------------------- """

class SchematicCapacitor(SchematicComponent):

    type = "Capacitor"

    def __init__(self, parent, x, y, sign, horizontal = True):
        super().__init__(parent, x, y, sign, horizontal)
        self.component = Capacitor(self)

    def drawComponent(self, qp):
        s = self.schematic.grid_size
        self.drawLeads(qp)
        self.drawLine(qp, s, 0, 1.8*s, 0)
        self.drawLine(qp, 1.8*s, -.75*s, 1.8*s, .75*s)
        self.drawLine(qp, 2.2*s, 0, 3*s, 0)
        self.drawLine(qp, 2.2*s, -.75*s, 2.2*s, .75*s)

""" -------------------------------------
    Inductor
    ------------------------------------- """

class SchematicInductor(SchematicComponent):

    type = "Inductor"

    def __init__(self, parent, x, y, sign, horizontal = True):
        super().__init__(parent, x, y, sign, horizontal)
        self.component = Inductor(self)

    def drawComponent(self, qp):
        s = self.schematic.grid_size
        self.drawLeads(qp)
        self.drawArc(qp, s, -.25*s, .5*s, .5*s, 0, 180)
        self.drawArc(qp, 1.5*s, -.25*s, .5*s, .5*s, 0, 180)
        self.drawArc(qp, 2*s, -.25*s, .5*s, .5*s, 0, 180)
        self.drawArc(qp, 2.5*s, -.25*s, .5*s, .5*s, 0, 180)


""" -------------------------------------
    Ground
    ------------------------------------- """

class SchematicGround(SchematicComponent):

    type = "Ground"

    def __init__(self, parent, x, y, sign, horizontal = True):
        super().__init__(parent, x, y, sign, horizontal)
        self.ground = True

    def drawLabel(self, qp):
        pass

    def drawLabelBox(self, qp):
        pass

    def edit(self):
        pass

    def getSolveData(self):
        return [["GND", "selected"]]

    def getConnections(self):
        s, x0, y0, w0, h0 = self.getDrawValues()
        sign = mp2oz(self.sign)
        return [(int(self.x + 2*sign*w0), int(self.y + 2*sign*h0))]

    def getCoreBoundingBox(self):
        s, x0, y0, w0, h0 = self.getDrawValues()
        w02 = self.sign == 1 and w0 or 0
        h02 = self.sign == 1 and h0 or 0
        return x0 - s*h0 + .2*s + .9*s*w02, y0 + .2*s - s*w0 + .9*s*h02, .6*s + s*h0, .6*s + s*w0

    def getBoundingBox(self):
        s, x0, y0, w0, h0 = self.getDrawValues()
        return x0 - s*h0, y0 - s*w0, 2*s, 2*s

    def drawComponent(self, qp):
        s = self.schematic.grid_size
        self.drawLine(qp, 0, 0, s, 0)
        self.drawLine(qp, s, -.5*s, s, .5*s)
        self.drawLine(qp, s*1.2, -.3*s, s*1.2, .3*s)
        self.drawLine(qp, s*1.4, -.1*s, s*1.4, .1*s)
        self.drawLine(qp, s*1.6, 0, s*1.6, 0)

""" -------------------------------------
    Component Lookup
    ------------------------------------- """

SchematicComponent.lookup = {
    "wire": SchematicWire,
    "resistor": SchematicResistor,
    "voltageSource": SchematicVoltageSource,
    "currentSource": SchematicCurrentSource,
    "ground": SchematicGround,
    "capacitor": SchematicCapacitor,
    "inductor": SchematicInductor
}
