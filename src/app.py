from qt import *
from mainWindow import MainWindow

app = QApplication([])
app.setApplicationName("Circuit Editor")
window = MainWindow(app)

window.show()
app.exec_()