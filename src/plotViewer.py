from qt import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import mplcursors
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

class PlotCanvas(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.figure = Figure()
        self.data = {}
        self.lines = {}
        self.legend = {}

        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.canvas.setFocus(True)
        self.canvas.setStyleSheet("background-color:transparent;")
        self.ax = self.figure.add_subplot(111)
        self.ax.patch.set_alpha(1)
        mplcursors.cursor(hover=True)

        self.clearButton = QPushButton("Clear Graph")
        self.clearButton.clicked.connect(self.clear)
        self.graphTypes = QHBoxLayout()
        self.graphVoltage = QRadioButton("Voltage")
        self.graphCurrent = QRadioButton("Current")
        self.graphPower = QRadioButton("Power")
        self.graphVoltage.toggled.connect(lambda: self.setPlotType(self.graphVoltage.text()))
        self.graphCurrent.toggled.connect(lambda: self.setPlotType(self.graphCurrent.text()))
        self.graphPower.toggled.connect(lambda: self.setPlotType(self.graphPower.text()))
        self.graphVoltage.setChecked(True)

        self.graphTypes.addWidget(self.graphVoltage)
        self.graphTypes.addWidget(self.graphCurrent)
        self.graphTypes.addWidget(self.graphPower)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.layout.addWidget(self.toolbar)
        self.layout.addLayout(self.graphTypes)
        self.layout.addWidget(self.clearButton)
        self.setLayout(self.layout)

    def addPlot(self, time, data):
        if not data["name"] in self.data:
            self.time = time
            self.data[data["name"]] = data
            line = None
            if self.measure == "Voltage" and "V" in data:
                line, = self.ax.plot(time, data["V"])
            elif self.measure == "Current" and "I" in data:
                line, = self.ax.plot(time, data["I"])
            elif self.measure == "Power" and "V" in data and "I" in data:
                p = []
                for x in range(len(data["V"])):
                    p.append(data["V"][x]*data["I"][x])
                line, = self.ax.plot(time, p)
            if line:
                self.lines.append(line)
                self.legend.append(data["name"])
            self.ax.legend(self.lines, self.legend)
            self.canvas.draw()

    def setPlotType(self, measure):
        self.measure = measure
        dataCopy = {}
        for d in self.data:
            dataCopy[d] = self.data[d]
        self.clear()
        for d in dataCopy:
            self.addPlot(self.time, dataCopy[d])

    def clear(self):
        self.data = {}
        self.lines = []
        self.legend = []
        self.ax.clear()
        self.figure.legends = []
        self.canvas.draw()

