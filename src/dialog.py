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
        msg = "Save Schematic"
        fileTypes = "Circuit Files (*.circuit);;All Files (*)"
        filename, _ = QFileDialog.getOpenFileName(window, msg, "", fileTypes)
        return filename


class EditComponent():

    def __init__(self, window, component):
        self.window = window
        self.component = component
        self.w, self.h = 300, 100
        self.dialog = QDialog()
        self.dialog.setWindowTitle("Edit " + component.schematicComponent.type)

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

        self.setValue = QDoubleSpinBox()
        self.setValue.setValue(self.component.value.value)
        self.setUnit = QComboBox()
        i = 0
        for v in component.value.unitPrefixes:
            self.setUnit.addItem(v + component.unit)
            if v == self.component.value.unitPrefix:
                self.setUnit.setCurrentIndex(i)
            i += 1

        self.form = QFormLayout(self.dialog)
        self.form.addRow("Name", self.nameEditor)
        self.form.addRow(component.measure, self.setValue)
        self.form.addRow("Unit", self.setUnit)
        self.form.addRow("", self.buttons)

        self.dialog.setGeometry(window.x() + window.width()/2 - self.w/2,
                          window.y() + window.height()/2 - self.h/2,
                          self.w, self.h)

    def okay(self):
        self.component.value.value = self.setValue.value()
        self.component.value.unitPrefix = self.setUnit.currentText()[:-1]
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