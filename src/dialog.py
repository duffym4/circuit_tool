from qt import *

class InfoDialogs():

    def about(window):
        text = "<center>" \
               "<h1>Circuit Analysis Tool</h1>" \
               "<p>Martin Duffy</p>" \
               "<p>Version 0.1</p>" \
               "</center>"
        QMessageBox.about(window, "About Circuit Analysis Tool", text)

class EditComponent():

    def __init__(self, window, component):
        self.window = window
        self.component = component
        self.w, self.h = 300, 100
        self.dialog = QDialog()
        self.dialog.setWindowTitle("Edit " + component.type)

        self.okayButton = QPushButton("ok", self.dialog)
        self.okayButton.clicked.connect(self.okay)
        self.cancelButton = QPushButton("delete", self.dialog)
        self.cancelButton.clicked.connect(self.cancel)
        self.buttons = QHBoxLayout()
        self.buttons.addWidget(self.okayButton)
        self.buttons.addWidget(self.cancelButton)

        self.setName = QLineEdit()
        self.setName.setText(component.namePrefix + "1")
        self.setName.setMaxLength(4)
        self.setName.setAlignment(Qt.AlignLeft)
        self.drawName = QCheckBox("show")
        self.nameEditor = QHBoxLayout()
        self.nameEditor.addWidget(self.setName)
        self.nameEditor.addWidget(self.drawName)

        self.setValue = QDoubleSpinBox()
        self.setValue.setValue(self.component.value)
        self.setUnit = QComboBox()
        for v in component.unitPrefixes:
            self.setUnit.addItem(v + component.unit)
        self.setUnit.setCurrentIndex(1)

        self.form = QFormLayout(self.dialog)
        self.form.addRow("Name", self.nameEditor)
        self.form.addRow(component.measure, self.setValue)
        self.form.addRow("Unit", self.setUnit)
        self.form.addRow("", self.buttons)

        self.dialog.setGeometry(window.x() + window.width()/2 - self.w/2,
                          window.y() + window.height()/2 - self.h/2,
                          self.w, self.h)

    def okay(self):
        self.component.value = self.setValue.value()
        self.component.unitPrefix = self.setUnit.currentText()[:-1]
        self.dialog.close()

    def cancel(self):
        self.window.schematic.components.remove(self.component.schematicComponent)
        self.dialog.close()

    def show(self):
        self.dialog.exec_()
