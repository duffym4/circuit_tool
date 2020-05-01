from qt import *
from validator import NameValidator

class InfoDialogs():

    def about(window):
        msg =  "<center>" \
               "<h1>Circuit Analysis Tool</h1>" \
               "<p>Martin Duffy</p>" \
               "<p>Version 0.1</p>" \
               "</center>"
        QMessageBox.about(window, "About Circuit Analysis Tool", msg)

    def changesLost(window):
        msg = "Are you sure? Changes will be lost!"
        yes, no = QMessageBox.Yes, QMessageBox.No
        return QMessageBox.question(window, '', msg, yes | no) == yes

    def saveFile(window):
        msg = "Save Schematic"
        fileTypes = "Circuit Files (*.circuit);;All Files (*)"
        filename, _ = QFileDialog.getSaveFileName(window, msg, "", fileTypes)
        return filename

    def openFile(window):
        msg = "Load Schematic"
        fileTypes = "Circuit Files (*.circuit);;All Files (*)"
        filename, _ = QFileDialog.getOpenFileName(window, msg, "", fileTypes)
        return filename

class CircuitProperties():

    def __init__(self, window):
        self.window = window
        self.schematic = window.schematic

        self.w, self.h = 300, 100
        self.dialog = QDialog()
        self.dialog.setWindowTitle("Circuit Properties")
        self.dialog.setGeometry(window.x() + window.width()/2 - self.w/2,
                          window.y() + window.height()/2 - self.h/2,
                          self.w, self.h)

        self.okayButton = QPushButton("ok", self.dialog)
        self.okayButton.clicked.connect(self.okay)
        self.cancelButton = QPushButton("cancel", self.dialog)
        self.cancelButton.clicked.connect(self.cancel)
        self.buttons = QHBoxLayout()
        self.buttons.addWidget(self.okayButton)
        self.buttons.addWidget(self.cancelButton)

        self.setDomain = QComboBox()
        self.setDomain.addItem("Time (t)")
        self.setDomain.addItem("Frequency (s)")
        if self.schematic.domain == "t":
            self.setDomain.setCurrentIndex(0)
        else:
            self.setDomain.setCurrentIndex(1)

        self.setDuration = QDoubleSpinBox()
        self.setDuration.setValue(self.schematic.simulationTime)


        self.form = QFormLayout(self.dialog)
        self.form.addRow("Domain", self.setDomain)
        self.form.addRow("Duration (s)", self.setDuration)
        self.form.addRow("", self.buttons)

        self.dialog.exec_()

    def okay(self):
        self.schematic.domain = self.setDomain.currentText()[-2:-1]
        self.schematic.simulationTime = self.setDuration.value()
        self.dialog.close()

    def cancel(self):
        self.dialog.close()

class EditComponent():

    def __init__(self, window, component):
        self.window = window
        self.component = component
        self.w, self.h = 300, 100
        self.dialog = QDialog()
        self.dialog.setWindowTitle("Edit " + component.schematicComponent.type)

        self.dialog.setGeometry(window.x() + window.width()/2 - self.w/2,
                          window.y() + window.height()/2 - self.h/2,
                          self.w, self.h)

        self.okayButton = QPushButton("ok", self.dialog)
        self.okayButton.clicked.connect(self.okay)
        self.cancelButton = QPushButton("delete", self.dialog)
        self.cancelButton.clicked.connect(self.cancel)
        self.buttons = QHBoxLayout()
        self.buttons.addWidget(self.okayButton)
        self.buttons.addWidget(self.cancelButton)

        self.nameValidator = NameValidator(self.window.schematic, self.component)

        self.setName = QLineEdit()
        self.setName.setText(self.component.name)
        self.setName.setValidator(self.nameValidator)
        self.setName.setMaxLength(4)
        self.setName.setAlignment(Qt.AlignLeft)
        self.drawName = QCheckBox("show")
        self.drawName.setCheckState(self.component.schematicComponent.drawName)
        self.nameEditor = QHBoxLayout()
        self.nameEditor.addWidget(self.setName)
        self.nameEditor.addWidget(self.drawName)

        self.setValueNumber = QDoubleSpinBox()
        numberMode = True
        try:
            self.setValueNumber.setValue(self.component.value.value)
        except:
            self.setValueNumber.setValue(1)
            numberMode = False

        self.setValueExpression = QLineEdit()
        self.setValueExpression.setText(str(self.component.value.value))
        self.setValue = QStackedLayout()
        self.setValue.addWidget(self.setValueNumber)
        self.setValue.addWidget(self.setValueExpression)
        if not numberMode:
            self.setValue.setCurrentWidget(self.setValueExpression)

        self.setUnit = QStackedLayout()
        self.setUnitMulti = QComboBox()
        i = 0
        for v in component.value.unitPrefixes:
            self.setUnitMulti.addItem(v + component.unit)
            if v == self.component.value.unitPrefix:
                self.setUnitMulti.setCurrentIndex(i)
            i += 1
        self.setUnitSimple = QLabel(component.unit)
        self.setUnit.addWidget(self.setUnitMulti)
        self.setUnit.addWidget(self.setUnitSimple)

        self.inputTypes = QHBoxLayout()
        self.inputNumber = QRadioButton("Number")
        self.inputExpression = QRadioButton("Expression")
        self.inputTypes.addWidget(self.inputNumber)
        self.inputTypes.addWidget(self.inputExpression)
        if numberMode:
            self.inputNumber.setChecked(True)
        else:
            self.inputExpression.setChecked(True)
        self.inputNumber.toggled.connect(lambda: self.inputTypeToggle(self.inputNumber))
        self.inputExpression.toggled.connect(lambda: self.inputTypeToggle(self.inputExpression))

        self.form = QFormLayout(self.dialog)
        self.form.addRow("Name", self.nameEditor)
        self.form.addRow(component.measure, self.setValue)
        self.form.addRow("Unit", self.setUnit)
        self.form.addRow("", self.inputTypes)
        self.form.addRow("", self.buttons)


    def inputTypeToggle(self, button):
        if button.text() == "Number" and button.isChecked():
            self.setValue.setCurrentWidget(self.setValueNumber)
            self.setUnit.setCurrentWidget(self.setUnitMulti)
        elif button.text() == "Expression" and button.isChecked():
            self.setValue.setCurrentWidget(self.setValueExpression)
            self.setUnit.setCurrentWidget(self.setUnitSimple)
        self.setValue.update()
        self.form.update()

    def okay(self):
        if self.setValue.currentWidget() == self.setValueNumber:
            self.component.value.value = self.setValueNumber.value()
            self.component.value.unitPrefix = self.setUnitMulti.currentText()[:-1]
        else:
            self.component.value.value = self.setValueExpression.text()
            self.component.value.unitPrefix = ""
        newName = self.setName.text()
        if not self.window.schematic.usedName(newName, self.component):
            self.component.name = newName
        self.component.schematicComponent.drawName = self.drawName.checkState()
        self.dialog.close()

    def cancel(self):
        self.window.schematic.components.remove(self.component.schematicComponent)
        self.dialog.close()

    def show(self):
        self.dialog.exec_()
