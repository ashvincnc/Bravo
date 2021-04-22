import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
#from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, QGridLayout, 
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import sys  
import os
from random import randint

class App(QDialog):

    def __init__(self):
        super().__init__()
        self.title = 'ventilator'
        self.left = 0
        self.top = 0
        self.width = 400
        self.height = 720
        self.initUI()
        self.graph()
       # self.graph2()
       # self.graph3()
        self.setStyleSheet("background-color: black;")
        self.update_parameters()

    def update_parameters(self):
        self.pressure_value = False 
        self.volume_value = False
        self.bpm_value = False
        self.fio2_value = False
        self.peep_value = False   
        
    def graph(self):
        self.graphWidget = pg.PlotWidget()
        self.x = list(range(100))  # 100 time points
        self.y = [randint(0,100) for _ in range(100)]  # 100 data points

        self.graphWidget.setBackground('#000000')

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()
        self.layout.addWidget(self.graphWidget,2,0,5,4)

    def update_plot_data(self):

        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        self.y = self.y[1:]  # Remove the first 
        self.y.append( randint(0,100))  # Add a new random value.

        self.data_line.setData(self.x, self.y)  # Update the data.

    def graph2(self):
        self.graphWidget = pg.PlotWidget()
        self.x2 = list(range(100))  # 100 time points
        self.y2 = [randint(0,100) for _ in range(100)]  # 100 data points

        self.graphWidget.setBackground('#000000')

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line =  self.graphWidget.plot(self.x2, self.y2, pen=pen)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data2)
        self.timer.start()
        #self.layout.addWidget(self.graphWidget,4,0,2,3)

    def update_plot_data2(self):

        self.x2 = self.x2[1:]  # Remove the first y element.
        self.x2.append(self.x2[-1] + 1)  # Add a new value 1 higher than the last.

        self.y2 = self.y2[1:]  # Remove the first 
        self.y2.append( randint(0,100))  # Add a new random value.

        self.data_line.setData(self.x2, self.y2)  # Update the data.

    def graph3(self):
        self.graphWidget = pg.PlotWidget()
        self.x = list(range(100))  # 100 time points
        self.y = [randint(0,100) for _ in range(100)]  # 100 data points

        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data3)
        self.timer.start()
        self.layout.addWidget(self.graphWidget,6,0,3,3)

    def update_plot_data3(self):

        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        self.y = self.y[1:]  # Remove the first 
        self.y.append( randint(0,100))  # Add a new random value.

        self.data_line.setData(self.x, self.y)  # Update the data.
    
     

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.createGridLayout()
        
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)

        self.setLayout(windowLayout)
        
        self.show()

    def pressure_set(self):

       
        self.slp = QSlider(Qt.Vertical, self) 
        self.slp.setRange(0, 100)  
        self.slp.setFocusPolicy(Qt.StrongFocus)
        self.slp.setPageStep(5)
        self.slp.valueChanged.connect(self.pupdateLabel)
        self.slp.setTickPosition(QSlider.TicksBelow)
        self.slp.setTickInterval(5)

        self.plabel = QLabel('0', self)
        self.plabel.setAlignment(Qt.AlignRight | Qt.AlignRight)
        self.plabel.setMinimumWidth(80)
        self.plabel.setFont(QFont('Arial', 25))
        self.plabel.setStyleSheet("color: white;  background-color: black")

        self.layout.addWidget( self.slp,2,6,4,1,alignment=Qt.AlignRight)
        self.layout.addWidget(self.plabel,6,6)

        self.update_val = QPushButton('Update')
        self.update_val.setFont(QFont('Verdana', 20))  
        self.update_val.setStyleSheet("background-color: orange")
        self.layout.addWidget(self.update_val,7,6)
        self.update_val.clicked.connect(self.update_setp)
        
    def update_setp(self):      
        self.slp.deleteLater()
        self.plabel.deleteLater()
        self.update_val.deleteLater()
        self.update_parameters()
    
    def pupdateLabel(self, value):      
        self.plabel.setText(str(value))
        self.lpressure.setText(str(value))
        self.pressure_value = str(value)

    def bpm_set(self):

        self.slbpm = QSlider(Qt.Vertical, self) 
        self.slbpm.setRange(0, 20)  
        self.slbpm.setFocusPolicy(Qt.StrongFocus)
        self.slbpm.setPageStep(5)
        self.slbpm.valueChanged.connect(self.bpmupdateLabel)
        self.slbpm.setTickPosition(QSlider.TicksBelow)
        self.slbpm.setTickInterval(5)

        self.bpmlabel = QLabel('0', self)
        self.bpmlabel.setAlignment(Qt.AlignRight | Qt.AlignRight)
        self.bpmlabel.setMinimumWidth(80)
        self.bpmlabel.setFont(QFont('Arial', 25))
        self.bpmlabel.setStyleSheet("color: white;  background-color: black")

        self.layout.addWidget( self.slbpm,2,6,4,1,alignment=Qt.AlignRight)
        self.layout.addWidget(self.bpmlabel,6,6)

        self.update_val = QPushButton('Update')
        self.update_val.setFont(QFont('Verdana', 20))  
        self.update_val.setStyleSheet("background-color: orange")
        self.layout.addWidget(self.update_val,7,6)
        self.update_val.clicked.connect(self.update_setbpm)
        
    def update_setbpm(self):      
        self.slbpm.deleteLater()
        self.bpmlabel.deleteLater()
        self.update_val.deleteLater()
        self.update_parameters()
    
    def bpmupdateLabel(self, value):      
        self.bpmlabel.setText(str(value))
        self.lbpm.setText(str(value))
        self.bpm_value = str(value)     

    def peep_set(self):

        self.slpeep = QSlider(Qt.Vertical, self) 
        self.slpeep.setRange(0, 20)  
        self.slpeep.setFocusPolicy(Qt.StrongFocus)
        self.slpeep.setPageStep(5)
        self.slpeep.valueChanged.connect(self.peepupdateLabel)
        self.slpeep.setTickPosition(QSlider.TicksBelow)
        self.slpeep.setTickInterval(5)

        self.peeplabel = QLabel('0', self)
        self.peeplabel.setAlignment(Qt.AlignRight | Qt.AlignRight)
        self.peeplabel.setMinimumWidth(80)
        self.peeplabel.setFont(QFont('Arial', 25))
        self.peeplabel.setStyleSheet("color: white;  background-color: black")

        self.layout.addWidget( self.slpeep,2,6,4,1,alignment=Qt.AlignRight)
        self.layout.addWidget(self.peeplabel,6,6)

        self.update_val = QPushButton('Update')
        self.update_val.setFont(QFont('Verdana', 20))  
        self.update_val.setStyleSheet("background-color: orange")
        self.layout.addWidget(self.update_val,7,6)
        self.update_val.clicked.connect(self.update_setpeep)
        
    def update_setpeep(self):      
        self.slpeep.deleteLater()
        self.peeplabel.deleteLater()
        self.update_val.deleteLater()
        self.update_parameters()
    
    def peepupdateLabel(self, value):      
        self.peeplabel.setText(str(value))
        self.lpeep.setText(str(value))
        self.peep_value = str(value)  

    def fio2_set(self):

        self.slfio2 = QSlider(Qt.Vertical, self) 
        self.slfio2.setRange(0, 100)  
        self.slfio2.setFocusPolicy(Qt.StrongFocus)
        self.slfio2.setPageStep(5)
        self.slfio2.valueChanged.connect(self.fio2updateLabel)
        self.slfio2.setTickPosition(QSlider.TicksBelow)
        self.slfio2.setTickInterval(5)

        self.fio2label = QLabel('0', self)
        self.fio2label.setAlignment(Qt.AlignRight | Qt.AlignRight)
        self.fio2label.setMinimumWidth(80)
        self.fio2label.setFont(QFont('Arial', 25))
        self.fio2label.setStyleSheet("color: white;  background-color: black")

        self.layout.addWidget( self.slfio2,2,6,4,1,alignment=Qt.AlignRight)
        self.layout.addWidget(self.fio2label,6,6)

        self.update_val = QPushButton('Update')
        self.update_val.setFont(QFont('Verdana', 20))  
        self.update_val.setStyleSheet("background-color: orange")
        self.layout.addWidget(self.update_val,7,6)
        self.update_val.clicked.connect(self.update_setfio2)
        
    def update_setfio2(self):      
        self.slfio2.deleteLater()
        self.fio2label.deleteLater()
        self.update_val.deleteLater()
        self.update_parameters()
    
    def fio2updateLabel(self, value):      
        self.fio2label.setText(str(value))
        self.lfio2.setText(str(value))
        self.fio2_value = str(value)      

    def value_set(self):
     
        self.sl = QSlider(Qt.Vertical, self) 
        self.sl.setRange(0, 100)  
        self.sl.setFocusPolicy(Qt.StrongFocus)
        self.sl.setPageStep(5)
        self.sl.valueChanged.connect(self.pupdateLabel)
        self.sl.setTickPosition(QSlider.TicksBelow)
        self.sl.setTickInterval(5)

        self.label = QLabel('0', self)
        self.label.setAlignment(Qt.AlignRight | Qt.AlignRight)
        self.label.setMinimumWidth(80)
        self.label.setFont(QFont('Arial', 25))
        self.label.setStyleSheet("color: white;  background-color: black")

        self.layout.addWidget( self.sl,2,6,4,1,alignment=Qt.AlignRight)
        self.layout.addWidget(self.label,6,6)

        self.update_val = QPushButton('Update')
        self.update_val.setFont(QFont('Verdana', 20))  
        self.update_val.setStyleSheet("background-color: orange")
        self.layout.addWidget(self.update_val,7,6)
        self.update_val.clicked.connect(self.update_set)

    def updateLabel(self, value):      
        self.label.setText(str(value))
        self.lpressure.setText(value)
        self.updated_value = str(value)

    def update_set(self):
        #print(self.updated_value) #Updated value
        if (self.pressure_value == True):
            self.lpressure.setText(self.updated_value)
            self.pressure_value = False
        if (self.volume_value == True):
            self.lvol.setText(self.updated_value)
            self.volume_value = False
        if(self.bpm_value == True):
            self.lbpm.setText(self.updated_value)
            self.bpm_value = False
        if(self.fio2_value == True):
            self.lfio2.setText(self.updated_value)
            self.fio2_value = False
        if(self.peep_value == True):
            self.lpeep.setText(self.updated_value)
            self.peep_value == False            

        self.sl.deleteLater()
        self.label.deleteLater()
        self.update_val.deleteLater()
        self.update_parameters()
    
    def bpm_update(self):
        self.bpm_value = True

    def fio2_update(self):
        self.fio2_value = True

    def peep_update(self):
        self.peep_value = True    

    def pressure_update(self):
        self.pressure_value = True

    def volume_update(self):
        self.volume_value = True      
        
    def updateLabel(self, value):      
        self.label.setText(str(value))
        self.updated_value = str(value)
        
    def ie_update(self):

      self.cb = QComboBox()
      self.cb.addItem("IE Values")
      self.cb.addItem("1:1")
      self.cb.addItem("1:2")
      self.cb.addItem("1:3")
      self.cb.addItem("1:4")
      self.cb.setFont(QFont('Verdana', 13))
      self.cb.setStyleSheet("color: black;  background-color: white") 
      self.cb.setGeometry(200, 150, 120, 40)  
      self.layout.addWidget(self.cb,7,4)
      self.cb.currentIndexChanged.connect(self.ie_updated)

    def ie_updated(self, value):
        #self.cb.deleteLater()
        self.ie_value = str(value)
        
       # if(self.ie_value == '1'):
        #    self.lie.setText('1:1')
        ##   self.lie.setText('1:2')
        #if(self.ie_value == '3'):
         #   self.lie.setText('1:3')
        #if(self.ie_value == '4'):
         #   self.lie.setText('1:4')            

    def trigger_update(self):

      self.cbtr = QComboBox()
      self.cbtr.addItem("Trigger")
      self.cbtr.addItem("-10")
      self.cbtr.addItem("-9")
      self.cbtr.addItem("-8")
      self.cbtr.addItem("-7")
      self.cbtr.addItem("-6")
      self.cbtr.addItem("-5")
      self.cbtr.addItem("-4")
      self.cbtr.addItem("-3")
      self.cbtr.setFont(QFont('Verdana', 15))
      self.cbtr.setStyleSheet("color: black;  background-color: white") 
      self.cbtr.setGeometry(200, 150, 120, 40)  
      self.layout.addWidget(self.cbtr,5,4)
      self.cbtr.currentIndexChanged.connect(self.trigger_updated)

    def trigger_updated(self, value):
        #self.cbtr.deleteLater()
        self.trigger_value = str(value)
       # if self.trigger_value == '1':
            #self.ltrigger.setText("-10")
        #if self.trigger_value == '2':
            #self.ltrigger.setText("-9")
        #if self.trigger_value == '3':
            #self.ltrigger.setText("-8")
        #if self.trigger_value == '4':
            #self.ltrigger.setText("-7")
        #if self.trigger_value == '5':
            #self.ltrigger.setText("-6")
        #if self.trigger_value == '6':
            #self.ltrigger.setText("-5")
        #if self.trigger_value == '7':
            #self.ltrigger.setText("-4")
        #if self.trigger_value == '8':
            #self.ltrigger.setText("-3")
                                        
        #print(self.trigger_value)

    def mode_update(self):

      self.md = QComboBox()
      self.md.addItem("Modes")
      self.md.addItem("None")
      self.md.addItem("PRVC")
      self.md.addItem("VC")
      self.md.addItem("PC")
      self.md.addItem("PS")
      self.md.addItem("SIMV(VC)+PS")
      self.md.addItem("SIMV(PC)+PS")
      self.md.setFont(QFont('Verdana', 15))
      self.md.setStyleSheet("color: black;  background-color: white") 
      self.md.setGeometry(200, 150, 120, 40)  
      self.layout.addWidget(self.md,3,4)
      self.md.currentIndexChanged.connect(self.mode_updated)

    def mode_updated(self, value):
        #self.md.deleteLater()
        self.mode_set = str(value)
        #if self.mode_set == '1':
           # self.lmode.setText('None')
        #if self.mode_set == '2':
           # self.lmode.setText('PRVC')
        #if self.mode_set == '3':
            #self.lmode.setText('VC')
        #if self.mode_set == '4':
            #self.lmode.setText('PC')
        #if self.mode_set == '5':
            #self.lmode.setText('PS')
        #if self.mode_set == '6':
            #self.lmode.setText('SIMV(VC)+PS')                    
        #if self.mode_set == '7':
            #self.lmode.setText('SIMV(PC)+PS')             

    def createGridLayout(self):
        self.horizontalGroupBox = QGroupBox() 
        self.layout = QGridLayout()
        #self.layout.setColumnStretch(6, 9)
       # self.layout.setColumnStretch(6, 9)     

        #Adding push buttons
        Bpressure = QPushButton('Pressure') #pressurepush button
        Bpressure.setGeometry(0, 0, 100, 40)
        Bpressure.setFont(QFont('Verdana', 15))  
        Bpressure.setStyleSheet("background-color: white")
        self.layout.addWidget(Bpressure,7,0)
        Bpressure.clicked.connect(self.pressure_set)
        Bpressure.clicked.connect(self.pressure_update)

        self.lpressure = QLabel("0")  #pressure label
        self.lpressure.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lpressure.setFont(QFont('Arial', 15))
        self.lpressure.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(self.lpressure,8,0)
        
        Bvol = QPushButton('Volume') #volumePushButton
        Bvol.setGeometry(0, 0, 100, 40)
        Bvol.setFont(QFont('Verdana', 15))
        Bvol.setStyleSheet("background-color: white")
        self.layout.addWidget(Bvol,7,1)
        Bvol.clicked.connect(self.volume_update)
        Bvol.clicked.connect(self.value_set)
        
        
        self.lvol = QLabel("0")  #volume label
        self.lvol.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lvol.setFont(QFont('Arial', 15))
        self.lvol.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(self.lvol,8,1)
  
        Bbpm = QPushButton('BPM')  #BPM PushButton
        Bbpm.setGeometry(0, 0, 100, 40)
        Bbpm.setFont(QFont('Verdana', 15))
        Bbpm.setStyleSheet("background-color: white")
        self.layout.addWidget(Bbpm,7,2)
        Bbpm.clicked.connect(self.bpm_set)
        Bbpm.clicked.connect(self.bpm_update)

        self.lbpm = QLabel("0")  #BPM label
        self.lbpm.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lbpm.setFont(QFont('Arial', 15))
        self.lbpm.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(self.lbpm,8,2)

        Bpeep = QPushButton('PEEP')  #peep_button
        Bpeep.setGeometry(0, 0, 100, 40)
        Bpeep.setFont(QFont('Verdana', 15))  
        Bpeep.setStyleSheet("background-color: white")
        self.layout.addWidget(Bpeep,7,3)
        Bpeep.clicked.connect(self.peep_set)
        Bpeep.clicked.connect(self.peep_update)

        self.lpeep = QLabel("0")  #peep label
        self.lpeep.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lpeep.setFont(QFont('Arial', 15))
        self.lpeep.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(self.lpeep,8,3)

        Bfio2 = QPushButton('fio2')  #fio2 Button
        Bfio2.setGeometry(0, 0, 100, 40)
        Bfio2.setFont(QFont('Verdana', 15))
        Bfio2.setStyleSheet("background-color: white")
        self.layout.addWidget(Bfio2,8,4)
        Bfio2.clicked.connect(self.fio2_set)
        Bfio2.clicked.connect(self.fio2_update)

        self.lfio2 = QLabel("0")  #fio2 label
        self.lfio2.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lfio2.setFont(QFont('Arial', 15))
        self.lfio2.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(self.lfio2,9,4)

        Bmode = QPushButton('Mode') #mode button
        Bmode.setGeometry(0, 0, 100, 400)
        Bmode.setFont(QFont('Verdana', 15))
        Bmode.setStyleSheet("background-color: white")
        self.mode_update()
        #self.layout.addWidget(Bmode,3,4)
        #Bmode.clicked.connect(self.mode_update)

        Btrigger = QPushButton('Trigger')  #trigger button
        Btrigger.setGeometry(0, 0, 100, 40)
        Btrigger.setFont(QFont('Verdana', 15))
        Btrigger.setStyleSheet("background-color: white")
        self.trigger_update()
        #self.layout.addWidget(Btrigger,4,4)
        #Btrigger.clicked.connect(self.trigger_update)

        self.ltrigger = QLabel("Trigger")  #trigger label
        self.ltrigger.setFont(QFont('Arial', 15))
        self.ltrigger.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(self.ltrigger,4,4)

        self.BIE = QPushButton('I:E')    #IE button
        self.BIE.setGeometry(0, 0, 100, 40)
        self.BIE.setFont(QFont('Verdana', 15))
        self.BIE.setStyleSheet("background-color: white")
        self.ie_update()
        #self.layout.addWidget(self.BIE,6,4)
        #self.BIE.clicked.connect(self.ie_update)

        self.lie = QLabel("IE")  #IE label
        self.lie.setFont(QFont('Arial', 15))
        self.lie.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(self.lie,6,4)

        self.lmode = QLabel("Modes")  #mode label
        self.lmode.setFont(QFont('Arial', 13))
        self.lmode.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(self.lmode,2,4)

        ratio = '1:1'                  #breath ratio label
        lbr = QLabel('Breath Ratio')
        lbr.setFont(QFont('Arial', 13))
        lbrdata = QLabel(ratio)
        lbrdata.setFont(QFont('Arial', 15))
        lbr.setStyleSheet("color: white;  background-color: black")
        lbrdata.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(lbr,2,5)
        self.layout.addWidget(lbrdata,3,5)

        pip = '0'                      #pip label       
        lbP = QLabel('PIP')
        lbP.setFont(QFont('Arial', 13))
        self.lbpdata = QLabel(pip)
        self.lbpdata.setFont(QFont('Arial', 15))
        lbP.setStyleSheet("color: white;  background-color: black")
        self.lbpdata.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(lbP,4,5)
        self.layout.addWidget(self.lbpdata,5,5)

        pmean = '0'                      #mean label    
        lbpmean = QLabel('P Mean')
        lbpmean.setFont(QFont('Arial', 13))
        self.lbpmeandata = QLabel(pmean)
        self.lbpmeandata.setFont(QFont('Arial', 15))
        lbpmean.setStyleSheet("color: white;  background-color: black")
        self.lbpmeandata.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(lbpmean,6,5)
        self.layout.addWidget(self.lbpmeandata,7,5)

        ti = '0'                          #Ti label
        lbti = QLabel('Ti')
        lbti.setFont(QFont('Arial', 13))
        self.lbtidata = QLabel(ti)
        self.lbtidata.setFont(QFont('Arial', 15))
        lbti.setStyleSheet("color: white;  background-color: black")
        self.lbtidata.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(lbti,8,5)
        self.layout.addWidget(self.lbtidata,9,5)

        ca = 'Exhale'                      #current activity label
        lbca = QLabel('Current Activity')
        lbca.setFont(QFont('Arial', 10))
        self.lbcadata = QLabel(ca)
        self.lbcadata.setFont(QFont('Arial', 15))
        lbca.setStyleSheet("color: white;  background-color: black")
        self.lbcadata.setStyleSheet("color: white;  background-color: black")
       # self.lbcadata.setText("Exhale")
       # self.lbcadata.setStyleSheet("border: 1px solid white;")
        self.layout.addWidget(lbca,1,6)
        self.layout.addWidget(self.lbcadata,2,6)

        Ve = '0'                           #Ve label
        lbve = QLabel('Ve')
        lbve.setFont(QFont('Arial', 10))
        self.lbvedata = QLabel(Ve)
        self.lbvedata.setFont(QFont('Arial', 15))
        lbve.setStyleSheet("color: white;  background-color: black")
        self.lbvedata.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(lbve,3,6)
        self.layout.addWidget(self.lbvedata,4,6)

        rr = '0'                            #RR label
        lbrr = QLabel('RR')
        lbrr.setFont(QFont('Arial', 10))
        self.lbrrdata = QLabel(rr)
        self.lbrrdata.setFont(QFont('Arial', 15))
        lbrr.setStyleSheet("color: white;  background-color: black")
        self.lbrrdata.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(lbrr,5,6)
        self.layout.addWidget(self.lbrrdata,6,6)

        peep = '0'                            #PEEP label
        lbpeep = QLabel('PEEP')
        lbpeep.setFont(QFont('Arial', 10))
        self.lbpeepdata = QLabel(peep)
        self.lbpeepdata.setFont(QFont('Arial', 15))
        lbpeep.setStyleSheet("color: white;  background-color: black")
        self.lbpeepdata.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(lbpeep,7,6)
        self.layout.addWidget(self.lbpeepdata,8,6)
      
        Bstart = QPushButton('Start')          #start button
        Bstart.setFont(QFont('Verdana', 15))
        Bstart.setStyleSheet("background-color: white")
        self.layout.addWidget(Bstart,9,6)
        
        self.lalarm = QLabel('Alarm')
        self.lalarm.setFont(QFont('Arial', 15))
        self.lalarm.setStyleSheet("color: white;  background-color: black")
        self.lalarm.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lalarm,0,0)
         
         
        self.lgas = QLabel('Gas-Pr')
        self.lgas.setFont(QFont('Arial', 15))
        self.lgas.setStyleSheet("color: white;  background-color: black")
        self.lgas.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lgas,0,1)

        self.lgasd = QLabel('Normal')
        self.lgasd.setFont(QFont('Arial', 15))
        self.lgasd.setStyleSheet("color: white;  background-color: green")
        self.lgasd.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lgasd,1,1)

        self.lapr = QLabel('O2-Pr')
        self.lapr.setFont(QFont('Arial', 15))
        self.lapr.setStyleSheet("color: white;  background-color: black")
        self.lapr.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lapr,0,2)

        self.laprd = QLabel('0')
        self.laprd.setFont(QFont('Arial', 15))
        self.laprd.setStyleSheet("color: white;  background-color: green")
        self.laprd.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.laprd,1,2)

        self.lpres = QLabel('Pressure')
        self.lpres.setFont(QFont('Arial', 15))
        self.lpres.setStyleSheet("color: white;  background-color: black")
        self.lpres.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lpres,0,4)

        self.lpresd = QLabel('0')
        self.lpresd.setFont(QFont('Arial', 15))
        self.lpresd.setStyleSheet("color: white;  background-color: green")
        self.lpresd.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lpresd,1,4)

        self.lmv = QLabel('VOL')
        self.lmv.setFont(QFont('Arial', 15))
        self.lmv.setStyleSheet("color: white;  background-color: black")
        self.lmv.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lmv,0,3)

        self.lmvd = QLabel('0')
        self.lmvd.setFont(QFont('Arial', 15))
        self.lmvd.setStyleSheet("color: white;  background-color: green")
        self.lmvd.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lmvd,1,3)


        self.lrr = QLabel('RR')
        self.lrr.setFont(QFont('Arial', 15))
        self.lrr.setStyleSheet("color: white;  background-color: black")
        self.lrr.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lrr,0,5) 

        self.lrrd = QLabel('0')
        self.lrrd.setFont(QFont('Arial', 15))
        self.lrrd.setStyleSheet("color: white;  background-color: green")
        self.lrrd.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lrrd,1,5) 

        self.llogo = QLabel('Bravo...')
        self.llogo.setFont(QFont('Gabriola', 25))
        self.llogo.setStyleSheet("color: maroon;  background-color: black")
        self.llogo.setAlignment(Qt.AlignLeft | Qt.AlignLeft)
        self.layout.addWidget(self.llogo,9,0) 
  
        
        self.lpower = QLabel('MAIN POWER')
        self.lpower.setFont(QFont('Arail', 13))
        self.lpower.setStyleSheet("color: white;  background-color: green")
        self.lpower.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lpower,0,6) 

        self.horizontalGroupBox.setLayout(self.layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())