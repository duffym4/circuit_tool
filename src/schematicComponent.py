from qt import *
from component import *
from dialog import *
import random, math

class SchematicComponent():

    """ -------------------------------------
        Initialization
        ------------------------------------- """

    def __init__(self, parent, x, y, sign, horizontal = True):
        self.x = x
        self.y = y
        self.horizontal = horizontal
        self.sign = sign
        self.schematic = parent
        self.overlapped = False
        self.selected = False
        self.colors = self.schematic.colors
        self.name = None
        self.wire = False

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
        qp.setFont(QFont('SansSerif', 10*(s/20)))
        if self.schematic.debug:
            self.drawBoundingBoxes(qp)
        qp.setPen(QPen(self.colors["standard"], math.floor(s/10)))
        if self.overlapped:
            qp.setPen(QPen(self.colors["overlapped"], math.floor(s/10)))
        elif self.selected:
            qp.setPen(QPen(self.colors["selected"], math.floor(s/10)))
        self.drawComponent(qp)

    """ -------------------------------------
        Painting
        ------------------------------------- """

    def drawBoundingBoxes(self, qp):
        s, x0, y0, w0, h0 = self.getDrawValues()
        qp.setPen(QPen(self.colors["boundingBox"], math.floor(s/10)))
        qp.drawRect(*self.getCoreBoundingBox())
        qp.setPen(QPen(self.colors["coreBoundingBox"], math.floor(s/10)))
        qp.drawRect(*self.getBoundingBox())

    def drawEndPoints(self, qp):
        s, x0, y0, w0, h0 = self.getDrawValues()
        qp.setPen(QPen(self.colors["coreBoundingBox"], math.floor(s/10)))
        qp.drawEllipse(x0 - s/4, y0 - s/4, s/2, s/2)
        qp.drawEllipse(x0 + 4*s*w0 - s/4, y0 + 4*s*h0 - s/4, s/2, s/2)

    def drawLeads(self, qp):
        s = self.schematic.grid_size
        self.drawLine(qp, 0, 0, s*.95, 0)
        self.drawLine(qp, 3.05*s, 0, 4*s, 0)

    def drawLabel(self, qp):
        s, x0, y0, w0, h0 = self.getDrawValues()
        lbl = ('%f' % self.component.value).rstrip('0').rstrip('.')
        unit = self.component.unitPrefix + self.component.unit
        align = Qt.AlignCenter
        if h0:
            align = Qt.AlignRight | Qt.AlignCenter
        box = QRectF(x0 + s*w0 - 2.5*s*h0,
                     y0 + (1.25*s)*h0 - (1.5*s)*w0,
                     2*s, s)
        qp.fillRect(box, self.colors["labelBox"])
        qp.setPen(QPen(self.colors["label"], math.floor(s/10)))
        qp.drawText(box, align, lbl + unit)

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
        x1, y1, w1, h1 = self.getCoreBoundingBox()
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
    Wires
    ------------------------------------- """

class SchematicWire(SchematicComponent):

    name = "Wire"

    def __init__(self, parent, x, y, length, sign, horizontal):
        super().__init__(parent, x, y, sign, horizontal)
        self.length = 0
        self.wire = True

    def drawComponent(self, qp):
        s, x0, y0, w0, h0 = self.getDrawValues()
        l = s*self.length*self.sign
        qp.drawLine(x0, y0, x0 + l*w0, y0 + l*h0)

    def edit(self):
        pass

    def drawEndPoints(self, qp):
        pass

    def drawLabel(self, qp):
        pass

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
        b = s*self.length*.5*(-self.sign + 1)
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

    def selecting(self, x, y):
        x1, y1, w1, h1 = self.getBoundingBox()
        if x > x1 and x < x1 + w1 and y > y1 and y < y1 + h1:
            return True

    def rotate(self):
        pass

""" -------------------------------------
    Voltage Source
    ------------------------------------- """

class SchematicVoltageSource(SchematicComponent):

    name = "Voltage Source"

    def __init__(self, parent, x, y, v, sign, horizontal = True):
        super().__init__(parent, x, y, sign, horizontal)
        self.component = VoltageSource(self, v)
        self.v = v

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

    name = "Current Source"

    def __init__(self, parent, x, y, i, sign, horizontal = True):
        super().__init__(parent, x, y, sign, horizontal)
        self.component = CurrentSource(self, i)
        self.i = i

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

    name = "Resistor"

    def __init__(self, parent, x, y, r, sign, horizontal = True):
        super().__init__(parent, x, y, sign, horizontal)
        self.component = Resistor(self, r)
        self.r = r

    def drawComponent(self, qp):
        s = self.schematic.grid_size
        self.drawLeads(qp)
        self.drawLine(qp, s, 0, 1.4*s, -2*s/3)
        self.drawLine(qp, 1.4*s, -2*s/3, 1.8*s, 2*s/3)
        self.drawLine(qp, 1.8*s, 2*s/3, 2.2*s, -2*s/3)
        self.drawLine(qp, 2.2*s, -2*s/3, 2.6*s, 2*s/3)
        self.drawLine(qp, 2.6*s, 2*s/3, 3*s, 0)

""" -------------------------------------
    Component Lookup
    ------------------------------------- """

SchematicComponent.lookup = {
    "resistor": SchematicResistor,
    "voltageSource": SchematicVoltageSource,
    "currentSource": SchematicCurrentSource,
    "wire": SchematicWire
}
