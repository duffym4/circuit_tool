from qt import *
from schematicComponent import *
import random, math

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
            "W": ["wire", "inserting"]
        }
        self.current = None
        self.components = []
        self.overlapped = []
        self.selected = None
        self.colors = {
            "grid": QColor(54, 65, 70),
            "standard": QColor(220, 200, 255),
            "overlapped": QColor(255, 100, 100),
            "selected": QColor(100, 255, 255),
            "boundingBox": QColor(155, 100, 100),
            "coreBoundingBox": QColor(100, 155, 155)
        }

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

    def mouseMoveEvent(self, e):
        self.mouse_x, self.mouse_y = e.x(), e.y()
        self.dragMove(e)
        if self.current:
            self.positionCurrent(e.x(), e.y())
        elif self.mode["mode"] == "navigation" and self.current == None:
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
        if self.current:
            self.current.draw(qp)

    """ -------------------------------------
        Controls
        ------------------------------------- """

    def changeMode(self, *mode):
        for m in self.mode:
            self.mode[m] = ""
        self.mode["mode"] = mode[0]
        for i in range(1, len(mode)):
            self.mode[mode[i-1]] = mode[i]
        if self.mode["mode"] == "component":
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
        if e.key() == Qt.Key_Escape:
            self.changeMode("navigation")
        else:
            if e.text() in self.componentShortcuts:
                self.changeMode("component", *self.componentShortcuts[e.text()])

    def navControls(self, e):
        if e.key() == Qt.Key_Right:
            self.offset_x -= 20
        elif e.key() == Qt.Key_Left:
            self.offset_x += 20
        elif e.key() == Qt.Key_Up:
            self.offset_y += 20
        elif e.key() == Qt.Key_Down:
            self.offset_y -= 20
        elif e.key() == Qt.Key_Backspace:
            if self.selected:
                self.components.remove(self.selected)
                self.selected = None
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
        self.offset_x -= delta/2
        self.offset_y -= delta/2
        self.grid_size = max(14, min(100, self.grid_size))

    """ -------------------------------------
        Components
        ------------------------------------- """

    def insertCurrent(self):
        if len(self.overlapped) > 0:
            return
        if self.mode["wire"] == "inserting":
            self.mode["wire"] = "resizing"
            return
        elif self.mode["wire"] == "resizing":
            self.mode["wire"] = "inserting"
            self.current.positive()
        self.components.append(self.current)
        if self.mode["component"] == "temporary":
            self.changeMode("navigation")
            self.selected = self.components[-1]
        else:
            h, s = self.current.horizontal, self.current.sign
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

    def resetCurrent(self, component, horizontal = True, sign = 1):
        if component != "temporary":
            self.current = SchematicComponent.lookup[component](self, 0, 0, 0, sign, horizontal)
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
        if not self.dragging:
            QApplication.restoreOverrideCursor()
        for c in self.components:
            c.selected = False
            if c.selecting(self.mouse_x, self.mouse_y):
                self.selected = c
                c.selected = True
                QApplication.setOverrideCursor(Qt.PointingHandCursor)
