from qt import *
from schematicComponent import *
from dialog import *
from util import *
from solver import Solver
import random, math, pickle

class SchematicEditor(QWidget):

    """ -------------------------------------
        Initialization
        ------------------------------------- """

    def __init__(self, parent):
        super().__init__()
        self.initUI()
        self.window = parent
        self.offset_x = 0
        self.offset_y = 0
        self.drag_x = 0
        self.drag_y = 0
        self.mouse_x = 0
        self.mouse_y = 0
        self.grid_size = 50
        self.dragging = False
        self.debug = False
        self.mode = {
            "mode": "navigation",
            "component": "",
            "wire": ""
        }
        self.componentShortcuts = {
            "R": ["resistor"],
            "V": ["voltageSource"],
            "I": ["currentSource"],
            "W": ["wire", "inserting"],
            "G": ["ground"]
        }
        self.actionShortcuts = {
            "ctrl": {
                Qt.Key_S: self.save,
                Qt.Key_L: self.load,
                Qt.Key_N: self.new,
                Qt.Key_Q: self.window.quit
            },
            Qt.Key_Space: self.solve,
        }
        self.current = None
        self.components = []
        self.overlapped = []
        self.selected = None
        self.colors = {
            "grid":             QColor(54, 65, 70),
            "standard":         QColor(220, 200, 255),
            "label":            QColor(255, 240, 255),
            "labelBox":         QColor(38, 50, 56, 155),
            "inspectBox":       QColor(0, 0, 0, 55),
            "overlapped":       QColor(255, 100, 100),
            "selected":         QColor(100, 255, 255),
            "new":              QColor(255, 240, 255, 100),
            "coreBoundingBox":  QColor(155, 100, 100),
            "boundingBox":      QColor(100, 155, 155)
        }
        self.zoom_min, self.zoom_max = 14, 100
        self.solver = Solver(self)

    def initUI(self):
        self.setMouseTracking(True)
        self.setGeometry(300, 300, 300, 190)
        self.show()
        self.adjustSize()

    """ -------------------------------------
        Events
        ------------------------------------- """

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawGrid(qp)
        self.drawComponents(qp)
        self.drawSolvedData(qp)

    def mouseMoveEvent(self, e):
        self.mouse_x, self.mouse_y = e.x(), e.y()
        self.dragMove(e)
        if self.current:
            self.positionCurrent(e.x(), e.y())
        elif self.mode["mode"] == "navigation" and self.current == None:
            self.selecting()
            if not self.dragging:
                QApplication.restoreOverrideCursor()
            if self.selected:
                QApplication.setOverrideCursor(Qt.PointingHandCursor)
        elif self.mode["mode"] == "inspect":
            self.selecting()
        self.update()

    def keyPressEvent(self, e):
        self.shortcuts(e)
        self.navControls(e)
        self.update()

    def mousePressEvent(self, e):
        if self.mode["mode"] == "component":
            self.componentMousePress(e)
        elif self.mode["mode"] == "navigation":
            self.grabComponent(e)
        self.dragStart(e, True)
        self.update()

    def mouseReleaseEvent(self, e):
        self.dragStart(e, False)
        self.update()

    def wheelEvent(self, e):
        self.zoom(e.angleDelta().y()/10)
        self.update()

    """ -------------------------------------
        Saving/Loading
        ------------------------------------- """

    def new(self):
        if len(self.components) == 0 or InfoDialogs.changesLost(self):
            self.components = []

    def save(self):
        fileName = InfoDialogs.saveFile(self)
        if fileName != "":
            with open(fileName, "wb") as f:
                pickle.dump(self.serialize(), f)

    def load(self):
        if len(self.components) == 0 or InfoDialogs.changesLost(self):
            fileName = InfoDialogs.openFile(self)
            if fileName != "":
                with open(fileName, "rb") as f:
                    self.deserialize(pickle.load(f))

    def serialize(self):
        data = {
            "components": [],
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "grid_size": self.grid_size
        }
        for x in self.components:
            data["components"].append(x.serialize())
        return data

    def deserialize(self, data):
        self.offset_x = data["offset_x"]
        self.offset_y = data["offset_y"]
        self.grid_size = data["grid_size"]
        self.components = []
        self.componentNames = {}
        for x in data["components"]:
            component = x["type"](self, 0, 0, 1, 1)
            component.deserialize(x)
            self.addComponent(component)

    """ -------------------------------------
        Painting
        ------------------------------------- """

    def drawGrid(self, qp):
        qp.setPen(self.colors["grid"])
        size = self.size()
        s = self.grid_size
        offset_x = self.offset_x % s
        offset_y = self.offset_y % s
        for x in range(-1, math.ceil(size.width()/s)):
            qp.drawLine(offset_x + x*s, 0, offset_x + x*s, size.height())
        for y in range(-1, math.ceil(size.height()/s)):
            qp.drawLine(0, offset_y + y*s, size.width(), offset_y + y*s)

    def drawComponents(self, qp):
        for c in self.components:
            c.draw(qp)
        for c in self.components:
            c.drawLabel(qp)
        if self.current:
            self.current.draw(qp)
            if self.mode["component"] == "temporary":
                self.current.drawLabel(qp)

    def drawSolvedData(self, qp):
        if self.mode["mode"] == "inspect" and self.selected:
            lr = self.mouse_x < self.window.width()/2
            tb = self.mouse_y < self.window.height()/2
            w, h = 500, 200
            box = [10 + lr*(self.window.width() - w - 20),
                       10 + tb*(self.window.height() - h - 50),
                       w, h]
            qp.fillRect(QRectF(*box), self.colors["inspectBox"])
            qp.setPen(QPen(self.colors["label"],  5, Qt.SolidLine))
            qp.drawRect(*box)
            qp.setPen(QPen(self.colors["label"], 10))
            align = Qt.AlignCenter
            qp.setFont(QFont('SansSerif', 20))
            qp.drawText(QRectF(*box), align, self.selected.getSolveData())

    """ -------------------------------------
        Controls
        ------------------------------------- """

    def changeMode(self, *mode):
        self.current = None
        for m in self.mode:
            self.mode[m] = ""
        self.mode["mode"] = mode[0]
        for i in range(1, len(mode)):
            self.mode[mode[i-1]] = mode[i]
        if self.mode["mode"] == "inspect":
            QApplication.setOverrideCursor(Qt.WhatsThisCursor)
        elif self.mode["mode"] == "component":
            self.resetCurrent(self.mode["component"])
            if self.mode["component"] == "wire":
                QApplication.setOverrideCursor(Qt.CrossCursor)
            else:
                QApplication.setOverrideCursor(Qt.OpenHandCursor)
        else:
            QApplication.restoreOverrideCursor()
            self.current = None
        self.overlapping(self.current)

    def shortcuts(self, e):
        ctrl = False
        if (e.modifiers() & Qt.ControlModifier):
            ctrl = True
        if e.key() == Qt.Key_Escape:
            self.changeMode("navigation")
        else:
            if e.text() in self.componentShortcuts:
                self.changeMode("component", *self.componentShortcuts[e.text()])
            if ctrl and e.key() in self.actionShortcuts["ctrl"]:
                self.actionShortcuts["ctrl"][e.key()]()
            elif e.key() in self.actionShortcuts:
                self.actionShortcuts[e.key()]()

    def navControls(self, e):
        if e.key() == Qt.Key_Right:
            self.offset_x -= 20
        elif e.key() == Qt.Key_Left:
            self.offset_x += 20
        elif e.key() == Qt.Key_Up:
            self.offset_y += 20
        elif e.key() == Qt.Key_Down:
            self.offset_y -= 20
        elif e.key() == Qt.Key_Backspace and self.mode["mode"] != "inspect":
            if self.selected:
                self.deleteComponent(self.selected)
            elif self.mode["component"] == "temporary":
                self.current = None
                self.changeMode("navigation")
        elif e.text() == "+" or e.text() == "=":
            self.zoom(10)
        elif e.text() == "-":
            self.zoom(-10)

    def componentMousePress(self, e):
        if e.button() == Qt.LeftButton:
            self.insertCurrent()
        elif e.button() == Qt.RightButton:
            self.rotateCurrent()

    def dragStart(self, e, value):
        if e.button() == Qt.MiddleButton or (self.mode["mode"] == "navigation" and e.button() == Qt.LeftButton):
            if value:
                QApplication.setOverrideCursor(Qt.DragMoveCursor)
            else:
                QApplication.restoreOverrideCursor()
            self.dragging = value
            self.drag_x = e.x()
            self.drag_y = e.y()

    def dragMove(self, e):
        if self.dragging:
            self.offset_x += e.x() - self.drag_x
            self.offset_y += e.y() - self.drag_y
            self.drag_x = e.x()
            self.drag_y = e.y()

    def zoom(self, delta):
        self.grid_size += delta
        self.grid_size = max(self.zoom_min, min(self.zoom_max, self.grid_size))
        if self.grid_size == self.zoom_min or self.grid_size == self.zoom_max:
            delta = 0
        self.offset_y -= (self.mouse_y-self.offset_y) / (self.grid_size)*delta
        self.offset_x -= (self.mouse_x-self.offset_x) / (self.grid_size)*delta

    """ -------------------------------------
        Solving
        ------------------------------------- """

    def solve(self):
        result = self.solver.reloadSchematic()
        if result:
            QMessageBox.about(self.window, "Error", str(result))
        else:
            self.changeMode("inspect")

    """ -------------------------------------
        Components
        ------------------------------------- """

    def addComponent(self, component):
        self.components.append(component)

    def deleteComponent(self, component):
        self.components.remove(component)
        self.selected = None

    def getNextName(self, prefix):
        names = self.getNames(prefix)
        nums = [0]
        for name in names:
            if name[1].isdigit():
                nums.append(int(name[1]))
        return prefix + str(min(set(range(1, len(nums) + 1)) - set(nums)))

    def usedName(self, name, component):
        prefix, rest = name[:1], name[1:]
        for other in self.getNames(prefix):
            if component != other[0] and other[1] == rest:
                return True
        return False

    def getNames(self, prefix):
        names = []
        for c in self.components:
            if hasattr(c, "component"):
                if c.component.name and c.component.name[:1] == prefix:
                    names.append((c.component, c.component.name[1:]))
        return names

    def insertCurrent(self):
        if len(self.overlapped) > 0:
            return
        if self.mode["wire"] == "inserting":
            self.mode["wire"] = "resizing"
            return
        elif self.mode["wire"] == "resizing":
            self.mode["wire"] = "inserting"
            self.current.positive()
        self.addComponent(self.current)
        self.current.new = False
        if self.mode["component"] == "temporary":
            self.changeMode("navigation")
            self.selected = self.components[-1]
        else:
            h, s = self.current.horizontal, self.current.sign
            self.current.edit()
            self.resetCurrent(self.mode["component"], h, s)

    def rotateCurrent(self):
        self.current.rotate()
        self.positionCurrent(self.mouse_x, self.mouse_y)

    def grabComponent(self, e):
        if e.button() == Qt.LeftButton:
            if not self.current and self.selected != None:
                self.changeMode("component", "temporary")
                self.current = self.selected
                self.components.remove(self.selected)
                self.selected = None
        elif e.button() == Qt.RightButton:
            if not self.current and self.selected != None:
                self.selected.edit()

    def resetCurrent(self, component, horizontal = True, sign = 1):
        if component != "temporary":
            self.current = SchematicComponent.lookup[component](self, 0, 0, sign, horizontal)
            self.current.new = True
            self.positionCurrent(self.mouse_x, self.mouse_y)

    def positionCurrent(self, x, y):
        if self.mode["wire"] == "resizing":
            self.current.resizeWire(x, y)
        else:
            self.current.position(x, y)
        self.overlapping(self.current)

    def overlapping(self, component):
        self.overlapped = []
        for c in self.components:
            c.overlapped = False
            if component and c.overlapping(component):
                self.overlapped.append(c)
                c.overlapped = True

    def selecting(self):
        self.selected = None
        for c in self.components:
            c.selected = False
            if c.selecting(self.mouse_x, self.mouse_y):
                self.selected = c
                c.selected = True
