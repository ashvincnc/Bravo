#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

In this example, we position two push
buttons in the bottom-right corner
of the window.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
import time
from PySide2.QtWidgets import (QWidget, QPushButton,
                             QHBoxLayout, QVBoxLayout, QApplication, QSpinBox, 
                             QGridLayout, QLabel, QComboBox, QSpacerItem, 
                             QGraphicsDropShadowEffect, QFormLayout,
                             QStackedWidget, QFrame, QMainWindow,
                             QLineEdit, QRadioButton)
from PySide2.QtCore import (Qt, QThread, Signal)
from PySide2.QtGui import QPalette, QColor, QFont
from controlPanel import ControlPanel

"""
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
"""

class SensorTest(QFrame):

    def __init__(self, parent):
        QFrame.__init__(self)
        parent.setWindowTitle('Sensor test')

        self.testSensor = QLabel("sensor test done")
        self.nextBtn = QPushButton("Next")
        self.nextBtn.clicked.connect(parent.gotoControlPage)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.testSensor)
        self.layout.addWidget(self.nextBtn)

        self.setLayout(self.layout)


class Login(QFrame):

    def __init__(self, parent):
        QFrame.__init__(self)
        parent.setWindowTitle('Patient details')

        self.patientName = QLineEdit()
        self.ageCombo = QComboBox()
        self.ageCombo.addItem("Male")
        self.ageCombo.addItem("Female")
        self.ageCombo.addItem("Other")

        self.ageBox = QLineEdit()

        formLayout = QFormLayout()
        formLayout.addRow(QLabel("Name:"), self.patientName)
        formLayout.addRow(QLabel("Gender:"), self.ageCombo)
        formLayout.addRow(QLabel("Age:"), self.ageBox)

        self.layout = QVBoxLayout()

        self.button = QPushButton('Next')
        self.button.clicked.connect(parent.gotoSensorTest)

        self.layout.addLayout(formLayout)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    def login(self):
        self.switch_window.emit()

class UI_MainWindow(QMainWindow):
    def __init__(self):
        super(UI_MainWindow, self).__init__()
        self.setWindowTitle('Main Window')

        self.Contents = QStackedWidget()
        self.Contents.addWidget(Login(self))
        self.Contents.addWidget(SensorTest(self))
        self.Contents.addWidget(ControlPanel(self))

        self.Contents.setCurrentIndex(2)
 
        # Left, Top, Width, Height
        #self.setGeometry(0, 0, 1000, 650)
        self.setWindowState(Qt.WindowMaximized)
        self.setCentralWidget(self.Contents)

    def gotoSensorTest(self):
        self.Contents.setCurrentIndex(1)

    def gotoControlPage(self):
        self.Contents.setCurrentIndex(2)

def main():
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Text, QColor(200, 200, 200))
    dark_palette.setColor(QPalette.Window, QColor(10, 10, 10))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Highlight, QColor(10, 130, 255))
    dark_palette.setColor(QPalette.HighlightedText, QColor(200, 200, 218))
    app = QApplication(sys.argv)
    app.setPalette(dark_palette)
    MainUI = UI_MainWindow()
    MainUI.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
