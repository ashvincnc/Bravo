import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSlot,pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread
import threading
import pyqtgraph as pg
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
import Adafruit_ADS1x15
sys.setrecursionlimit(10**3)
adc = Adafruit_ADS1x15.ADS1115(address=0x48)
GAIN = 1
import sys  
import os
import json
import serial
import time
global ini
ini = 0
global o2_val
o2_val = 0

class breathWorker(QThread):
    
    stopSignal = pyqtSignal()
    running = False
    breathStatus = 0
    currentPressure = 0
    pressureCycleValue = 0


    def __init__(self):
        super().__init__()
 
        self._exhale_event = threading.Event()
        self._inhale_event = threading.Event()

        GPIO.setup(12, GPIO.OUT)
        GPIO.setup(13, GPIO.OUT)
        
        GPIO.setup(14, GPIO.OUT)
        
        GPIO.setup(26, GPIO.OUT)
        GPIO.output(14,GPIO.HIGH)
        self.o2PWM = GPIO.PWM(12, 50)
        self.pPWM = GPIO.PWM(13, 50)
###
        
    def update_pwm_Data(self):

        global volume_pdata


        volume_data = int(volume_pdata)*20
        print('v_data',volume_pdata)
        oxyPercent = 1400
        self.pressureCycleValue = self.readPressureValues(volume_data)            
        print("pressureCycleValue")
        print(self.pressureCycleValue)  
        

    def stop(self):
        print("stopping breather thread")
        self.pPWM.ChangeDutyCycle(0)
        self.o2PWM.ChangeDutyCycle(0)
        print('duty_cycle_off') 
        GPIO.output(14,GPIO.HIGH)
        GPIO.output(26,GPIO.HIGH)
        self.running = False

    def run(self):
        
        GPIO.output(14,GPIO.LOW)
        self.o2PWM.start(0)
        self.pPWM.start(0)
        QThread.msleep(1)
        
        while self.running:
                
                self.pwm_in()
        while(self.running == False):
                
                self.pwm_out()
                break
        
               
   

    def pwm_in(self):
                global graph
      #          print("self.running.loop")  
                graph = 0               
                self.pPWM.ChangeDutyCycle(self.pressureCycleValue)
                self.o2PWM.ChangeDutyCycle(71)                
                GPIO.output(26,GPIO.HIGH)
                GPIO.output(14,GPIO.LOW)
                self.breathStatus = 0
  

    def pwm_out(self):
                global graph
                graph = 1
                self.o2PWM.ChangeDutyCycle(0)
                self.pPWM.ChangeDutyCycle(0)
    #            print('out')
                GPIO.output(26,GPIO.LOW)
                self.breathStatus = 1

 
    def readPressureValues(self, pressValue):
        pressValuFromJson = 0
        with open('pressure.json') as data_file:
            data = json.load(data_file)
            for restaurant in data['PressureValues']:
                minSatisfied = int(restaurant['PressureValue']['min'])<=int(pressValue)
                maxSatisfied = int(restaurant['PressureValue']['max'])>=int(pressValue)
                if(minSatisfied and maxSatisfied):
                    print("pressVal",restaurant['PressureValue']['value'])
                    pressValuFromJson = restaurant['PressureValue']['value']
            return pressValuFromJson
        
class backendWorker(QThread):
    threadSignal = pyqtSignal(dict)
    stopSignal =  pyqtSignal()
    dataUpdate = None
    firstLaunch = True
    currentVolData = 0


    def __init__(self, startParm):
        super().__init__()
        #self.running = True
        self.startParm = startParm   # Initialize the parameters passed to the task
        print('startParm')
        self.dataDict = {
            "curr_act" : 0,
            "o2conc" : [],
            "AirV" : [],
            "Dpress+" : [],
            "Dpress-" : [],
            "press+" : [],
            "press-" : [],
            "co2" : [],
            "temp" : [],
            "hum" : []
        }
        #GPIO.setup(4, GPIO.OUT)

    def stop(self):
        print("stopping thread")
        self.running = False

    def getdata(self):

        global firstvalue
        global graph
        global ini,o2_val,test
        currentPressure = 0
        ko = 0
        
      #  print('getdata_init')
        read_ser = []

        
#        print('getdata')
        data = [0]*4

        endtime = time.time()+0.1
        while(time.time()<endtime):
            
            for i in range(4):
                try:  
                    data[i] = adc.read_adc(i, gain=GAIN)
           #         print('i ,data',i,data[i])
                except:
                    print('i2c error')
                
 
            #sleep(0.3)
            pressurel = []
            
            pressurel.append(int(data[0])/8000)

        
  
        pressurel.sort(reverse = True)

        
            
        if(graph == 0):

            if(ini == 0):
                    firstvalue = pressurel[0]
                    print('firstvalue',firstvalue)
                    currentPressure = firstvalue
                    ini += 1

            else:
                    nextvalue = pressurel[0]
                    if(nextvalue > firstvalue):
                        currentPressure = nextvalue
                        firstvalue = currentPressure
                    if(nextvalue < firstvalue):
                        currentPressure = firstvalue
                        firstvalue = currentPressure
     
            if (currentPressure < pressurel[0]):
                currentPressure = pressurel[0]
            else:
               currentPressure = firstvalue

            press = currentPressure     
            prs = "{:.1f}".format(press)
            pr = float(prs)

            pressure = ((pr-2.5)/0.2)

            pressure = (round(pressure,1))
            test = pressure*5
            print('testin',test)
            self.dataDict["Dpress+"].append(pressure*5)   
        if (graph == 1):

            currentPressure = int(data[0])/8000


            
            press = currentPressure

            prs = "{:.1f}".format(press)
            pr = float(prs)

            pressure = ((pr-2.5)/0.2)

            pressure = (round(pressure,1))
            test = pressure*5
            print('testout',test)

            self.dataDict["Dpress+"].append(pressure*5)
        #print('sen',data )
        self.dataDict["o2conc"].append(float(data[3])*0.1276)
        o2_val = self.dataDict["o2conc"][-1]

        return self.dataDict
        

 

    def run(self):
        global data_m
        # Do something...
        if self.firstLaunch :
         #   self.initSerData()
            self.firstLaunch=False
        #self.sendValues()
        print("starting thread")
        while self.running:
            data_m = self.getdata()
        #    print('data_m',data_m)
   #         if data_m != None:
   #             self.threadSignal.emit(data_m)

            QThread.msleep(10)
        #GPIO.output(4,GPIO.LOW)
        print("stopped thread")
 #       print('bworker',data_m)
        #self.threadSignal.emit(self.startParm)


class App(QFrame):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 layout'
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 100
        self.initUI()
        self.bthThread = breathWorker()
        self.bthThread.stopSignal.connect(self.bthThread.stop)
        self.beThread = backendWorker('hello')
        self.beThread.stopSignal.connect(self.beThread.stop)
        
    def initUI(self):
        global start
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setStyleSheet("background-color: black;")
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)

        self.timer.timeout.connect(self.update_label)
        self.timer.start()
        
        self.createGridLayout()
        
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)
        
        self.show()
    
    def update_label(self):
        global test,o2_val,test
        try:
            o2_val = round(o2_val,1)
            if(self.off == 0):
                self.pressurelabel.setText("pressure: " + str(test))
                self.o2label.setText("o2: " + str(o2_val))
            if(self.off == 1):
                self.pressurelabel.setText("pressure: " + '-')
                self.o2label.setText("o2: " + '-')
        except:
            f = 0

    def on_process(self):

        self.bthThread.update_pwm_Data()
        self.beThread.running = True
        self.bthThread.running = True
        self.beThread.start()
        self.bthThread.start()
        self.on = 1
        self.off = 0
    def off_process(self):

        print('Stop')
        self.on = 0
        self.off = 1
        #time.sleep(1)
        self.beThread.stopSignal.emit()
        self.bthThread.stopSignal.emit()
        
        GPIO.output(14,GPIO.HIGH)
        GPIO.output(26,GPIO.HIGH)
      

    def stop_action(self):
        Bstart = QPushButton('Start')          #start button
        Bstart.setFont(QFont('Arial', 30))
        Bstart.setStyleSheet("background-color: white")
        Bstart.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.pressurelabel.setText("pressure: " + '-')#str(test))
        self.o2label.setText("o2: " + '-')#str(o2_val))
        self.flowlabel.setText('Flow:'+'-')       
        Bstart.clicked.connect(self.on_process)
        self.layout.addWidget(Bstart,5,3)
        Bstart.clicked.connect(self.stop)

    def stop(self):
        self.bstop = QPushButton('STOP')
        self.bstop.setFont(QFont('Arial', 30))
        self.bstop.setStyleSheet("background-color: grey")
        self.bstop.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.layout.addWidget(self.bstop,5,3)
        self.bstop.clicked.connect(self.off_process)
        self.bstop.clicked.connect(self.stop_action)      
    def update_flow(self):
        global volume_pdata, value
        volume_pdata = value
        self.flowlabel.setText('Flow:'+str(volume_pdata))

         
    def createGridLayout(self):
        self.horizontalGroupBox = QGroupBox()
        self.layout = QGridLayout()
        self.layout.setColumnStretch(1, 4)
        self.layout.setColumnStretch(2, 4)
        
         # creating QDial object
        dial = QDial(self)
        dial.setStyleSheet(" background-color: #20BEC6")
        # adding action to the dial
        dial.valueChanged.connect(lambda: dial_method())

        # creating a label
        self.label = QLabel("Flow Value", self)
        self.label.setFont(QFont('Arial', 30))
        self.label.setStyleSheet("color: white;  background-color: black")
        self.label.setAlignment(Qt.AlignRight | Qt.AlignRight)

        #o2 label
        self.o2label = QLabel("o2:")
        self.o2label.setFont(QFont('Arial', 30))
        self.o2label.setStyleSheet("color: white;  background-color: black")

        self.pressurelabel = QLabel("Pressure:")
        self.pressurelabel.setFont(QFont('Arial', 30))
        self.pressurelabel.setStyleSheet("color: white;  background-color: black")

        self.flowlabel = QLabel("Flow")
        self.flowlabel.setFont(QFont('Arial', 30))
        self.flowlabel.setStyleSheet("color: white;  background-color: black")

        Bstart = QPushButton('Start')          #start button
        Bstart.setFont(QFont('Arial', 30))
        Bstart.setStyleSheet("background-color: white")
        Bstart.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        Bstart.clicked.connect(self.on_process)
        Bstart.clicked.connect(self.stop)

        Bupdate = QPushButton('Update')          #start button
        Bupdate.setFont(QFont('Arial', 30))
        Bupdate.setStyleSheet("background-color: white")
        Bupdate.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        Bupdate.clicked.connect(self.update_flow)
        # making label multiline
        self.label.setWordWrap(True)

        # method called by the dial
        def dial_method():
            global volume_pdata, value

            value = dial.value()
         #   print('vol',volume_pdata)
             
            self.label.setText("Flow value: " + str(value))
            

        dummy = QLabel("HFFF")
        dummy.setStyleSheet("color: black;  background-color: black")

        self.layout.addWidget(dial, 2,0,2,2)
        self.layout.addWidget(self.label, 4,0)
        self.layout.addWidget(self.o2label, 2,3)
        self.layout.addWidget(self.pressurelabel, 3,3)
        self.layout.addWidget(self.flowlabel, 4,3)
        #self.layout.addWidget(dummy,2,5,2,2)
        self.layout.addWidget(Bstart,5,3)
        self.layout.addWidget(Bupdate,5,0)	
  
        self.horizontalGroupBox.setLayout(self.layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
