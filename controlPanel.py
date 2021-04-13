from PySide2.QtWidgets import (QWidget, QPushButton,
                             QHBoxLayout, QVBoxLayout, QApplication, QSpinBox,
                             QGridLayout, QLabel, QComboBox, QSpacerItem,
                             QGraphicsDropShadowEffect, QFormLayout,
                             QStackedWidget, QFrame, QMainWindow,
                             QLineEdit, QRadioButton, QSlider, QSizePolicy)
from PySide2.QtCore import (Qt, QThread, Signal)
from PySide2.QtGui import QPalette, QColor, QFont



from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

import serial
import time
import threading
import random

from random import randint

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

import sys

sys.setrecursionlimit(10**3)

# importing the module
import json
global a
a = 0
global firstvalue
global graph
graph = 0
class qwidgetContainer(QWidget):
    def __init__(self, widget1, widget2, parent, BGc = None):
        super().__init__(parent=parent)
        print(type(widget1))

        self.centerLayout = QVBoxLayout(self)
        self.testWidget = QFrame()
        #testWidget.setFixedSize(100,100)
        if BGc != None:
            self.testWidget.setObjectName("myWidget")
            self.testWidget.setStyleSheet("#myWidget {background-color:#c7b198;}")
        self.widget1 = widget1
        self.widget2 = widget2
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.widget1)
        self.layout.addWidget(self.widget2)
        self.testWidget.setLayout(self.layout)
        self.centerLayout.addWidget(self.testWidget)

"""
class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, facecolor=(0.8,.80,.80), edgecolor=(1,1,1), dpi=100):
        #fig = Figure(figsize=(width, height), dpi=dpi)
        fig = Figure(facecolor=facecolor, edgecolor=edgecolor, dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
"""

class Tuner(QFrame):
    def __init__(self, name, Range=[0, 100, 1], default=0):
        QFrame.__init__(self)
        self.value = int(default)
        self.min = int(Range[0])
        self.max = int(Range[1])
        self.fine = 0
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignBaseline | Qt.AlignHCenter)
        self.setLayout(layout)
        self.slide = QSlider(Qt.Vertical)
        self.slide.setMinimum(int(Range[0]))
        self.slide.setMaximum(int(Range[1]))
        self.slide.setTickPosition(QSlider.NoTicks)
        #self.dial1.setRange(dialRange[0], dialRange[1], dialRange[2])
        self.slide.setValue(default)
        self.slide.setStyleSheet( """
        QSlider::groove:vertical {
        border: 1px solid #262626;
        width: 20px;
        background: #393939;
        margin: 42px 42px;}
        QSlider::handle:vertical {
        background: #22B14C;
        border: 5px solid #B5E61D;
        width: 60px;
        height: 40px;
        margin: -5px -22px;
        }""")

        """QSlider::groove:vertical {
        background-color: lightblue;
        border: 10px solid;
        width: 30px;
        margin: -12px -12px;
        }
        QSlider::handle:vertical {
        background-color: blue;
        border: 10px solid;
        height: 40px;
        width: 40px;
        margin: -12px -12px;
        }"""
        #self.dial1.valueChanged.connect(self.sliderMoved)

        self.buttonP = QPushButton("+")
        self.buttonN = QPushButton("-")
        self.buttonP.setFont(QFont('Times', 30))
        self.buttonN.setFont(QFont('Times', 30))
        self.buttonP.setStyleSheet("QPushButton { border-radius : 10; background-color: white; }")
        self.buttonN.setStyleSheet("QPushButton { border-radius : 10; background-color: white; }")

        self.label1 = QLabel('0')
        self.label1.setAlignment(Qt.AlignCenter)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.buttonN, 1)
        hbox.addWidget(self.label1, 2)
        hbox.addWidget(self.buttonP, 1)
        hbox.addStretch(1)

        self.label2 = QLabel(name)
        self.label2.setAlignment(Qt.AlignCenter)

        sliderbox = QHBoxLayout()
        sliderbox.addWidget(self.slide)

        layout.addWidget(self.label2, 1)
        layout.addLayout(hbox, 1)
        layout.addStretch(1)
        #layout.addStretch(1)
        #layout.addStretch(0)
        layout.addLayout(sliderbox, 3)
        self.setFrameStyle(QFrame.Box | QFrame.Sunken);
        self.setLineWidth(1);
        self.setMidLineWidth(3);

class dataStack:
    def __init__(self, name, index, dial, button, obj):
        self.name = name
        self.tuner = dial
        self.button = button
        self.idx = index

        self.tuner.slide.valueChanged.connect(lambda:obj.sliderMov(self.idx))
        self.tuner.buttonP.clicked.connect(lambda:obj.buttonPlus(self.idx))
        self.tuner.buttonN.clicked.connect(lambda:obj.buttonMinus(self.idx))
        self.tuner.setVisible(False)

class breathWorker(QThread):
    sigDataupdate = Signal(dict)
    stopSignal = Signal()
    running = False
    breathStatus = 0
    currentPressure = 0
    pressureCycleValue = 0
    global graph

    def __init__(self):
        super().__init__()
        print("setup pwm ")

        # self._key_lock = threading.Lock()
        self._exhale_event = threading.Event()
        self._inhale_event = threading.Event()

        GPIO.setup(40, GPIO.OUT)
        GPIO.setup(41, GPIO.OUT)
        
        GPIO.setup(14, GPIO.OUT)
        
        GPIO.setup(26, GPIO.OUT)
        GPIO.output(14,GPIO.HIGH)
        self.o2PWM = GPIO.PWM(40, 50)
        self.pPWM = GPIO.PWM(41, 50)


    def updateData(self, data):
        #self._key_lock.acquire()
        self.o2DC = int(data['fio2'])
        self.pDC = int(data['pressure'])
        print("Volume",data['volume_tuner'])
        print("Value from tuner", data['volume_tuner'])
        print("Oxygen Set: ",data['fio2'])
        pressPercent = 0
        oxyPercent = 0
        if((int(data['fio2']))>21 and (int(data['fio2']))>50):
            oxy_value = float(data['fio2'])/100
            pressPercent = float(data['volume_tuner']) * (1-oxy_value)
            oxyPercent = float(data['volume_tuner']) * oxy_value
        elif((int(data['fio2']))>21 and (int(data['fio2']))<51):
            oxy_value = float(data['fio2'])/100
            pressPercent = float(data['volume_tuner']) * oxy_value
            oxyPercent = float(data['volume_tuner']) * (1-oxy_value)
        else:
            pressPercent = data['volume_tuner']
            oxyPercent = 0

        # if((int(data['fio2']))>21):
        #     print("Came to If")
        #     oxy_value = float(data['fio2'])/100
        #     print("oxy_value: ", oxy_value)
        #     print("prss_value: ", 1-oxy_value)
        #     print("Pressure: ", float(data['volume_tuner']) * (1-oxy_value))
        #     print("Oxygen: ", float(data['volume_tuner']) * oxy_value)
        #     pressPercent = float(data['volume_tuner']) * (1-oxy_value)
        #     oxyPercent = float(data['volume_tuner']) * oxy_value
        # else:
        #     print("Came to Else")
        #     pressPercent = 1
        #     oxyPercent = 0

        print("Percents: ", pressPercent,oxyPercent)
        self.pressureCycleValue = self.readPressureValues(pressPercent,oxyPercent)
        print("pressureCycleValue")
        print(self.pressureCycleValue)
        self.in_t = data['intime'] / 1000
        self.out_t = data['outtime'] /1000
        print("In and out" + str(self.in_t) + str(self.out_t))
        self.peep = int(data['peep'])

        #self._key_lock.release()

    def stop(self):
        print("stopping breather thread")
        GPIO.output(14,GPIO.HIGH)
        GPIO.output(26,GPIO.HIGH)
        self.running = False

    def run(self):
        global graph
        GPIO.output(14,GPIO.LOW)
        self.o2PWM.start(0)
        self.pPWM.start(0)
        print("starting breather thread"+ str(self.o2DC)+str(self.pDC)+str(self.in_t)+str(self.out_t)+str(self.peep))
     #   data=serial.Serial("/dev/ttyUSB0",9600)
     #   data.braudrate = 9600
       # data =  serial.Serial(port,9600)
        QThread.msleep(10)
        while self.running:
                print("self.running.loop")
      #          msg = data.readline()
       #         print(msg)
            #self._key_lock.acquire()
            # self.pPWM.ChangeDutyCycle(self.pDC)
            # self.o2PWM.ChangeDutyCycle(self.pressureCycleValue)
            # self.pPWM.ChangeDutyCycle(self.pressureCycleValue)
            # self.o2PWM.ChangeDutyCycle(100)
                self.pPWM.ChangeDutyCycle(self.pressureCycleValue[0])
                self.o2PWM.ChangeDutyCycle(self.pressureCycleValue[1])
            # self.pPWM.ChangeDutyCycle(100)
                GPIO.output(26,GPIO.HIGH)
                GPIO.output(14,GPIO.LOW)
                self.breathStatus = 0
                graph = 0
                #GPIO.output(12,GPIO.HIGH)
                #GPIO.output(19,GPIO.HIGH)
                # QThread.msleep(self.in_t)
                self._inhale_event.wait(timeout=self.in_t)
                print(self.peep)
                self.o2PWM.ChangeDutyCycle(self.peep)
                self.pPWM.ChangeDutyCycle(self.peep)
                GPIO.output(26,GPIO.LOW)
                # GPIO.output(14,GPIO.HIGH)
                self.breathStatus = 1
                graph = 1
                #GPIO.output(12,GPIO.LOW)
                #GPIO.output(19,GPIO.LOW)
                # QThread.msleep(self.out_t)
                self._exhale_event.wait(timeout=self.out_t)

                #self._key_lock.release()
            #self.o2PWM.stop()
            #self.pPWM.stop()

    # Reading Other File
    def readPressureValues(self, pressValue, oxValue):
        pressValuFromJson = 0
        oxyValuFromJson = 0
        with open('pressure.json') as data_file:
            data = json.load(data_file)
            for restaurant in data['PressureValues']:
                minSatisfied = int(restaurant['PressureValue']['min'])<=int(pressValue)
                maxSatisfied = int(restaurant['PressureValue']['max'])>=int(pressValue)
                if(minSatisfied and maxSatisfied):
                    print("pressVal",restaurant['PressureValue']['value'])
                    pressValuFromJson = restaurant['PressureValue']['value']
            for oxyValue in data['OxygenValues']:
                minSatisfied = int(oxyValue['OxygenValue']['min'])<=int(oxValue)
                maxSatisfied = int(oxyValue['OxygenValue']['max'])>=int(oxValue)
                if(minSatisfied and maxSatisfied):
                    print("Oxygen",oxyValue['OxygenValue']['value'])
                    oxyValuFromJson = oxyValue['OxygenValue']['value']

            return pressValuFromJson,oxyValuFromJson


class backendWorker(QThread):
    threadSignal = Signal(dict)
    stopSignal = Signal()
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

    def initSerData(self):
        self.ser = serial.Serial("/dev/ttyUSB0",9600)  #change ACM number as found from ls /dev/tty/ACM*
        #self.ser1 = serial.Serial("/dev/ttyUSB1",9600)
        self.ser.baudrate=9600
        #self.ser1.baudrate=9600

    def sendValues(self):
        #GPIO.output(4,GPIO.HIGH)
        #time.sleep(0.2)
        #GPIO.output(pin,GPIO.LOW)
        data2transfer = self.dataUpdate["pressure"]+','+self.dataUpdate["intime"]+','+self.dataUpdate["outtime"]+','+self.dataUpdate["peep"]+','+self.dataUpdate["fio2"]
        print("DEBUG: "+data2transfer)
        #self.ser1.write(data2transfer.encode())

    def getdata(self):
        global a
        global firstvalue
        global graph
        print('getdata_init')
        read_ser = []
        endtime = time.time()+0.1
        while(time.time()<endtime):
            data = self.ser.readline()
            data_s = data.rstrip()
            data_string = str(data_s)
            data = list(data_string.split(","))
            pressurel = []
            pressurel.append(int(data[3]))

            
          #      currentPressure = firstvalue
           
        pressurel.sort(reverse = True)
        print('test',pressurel[0])
        if(graph == 0):
            print('Inhaling')
            if(a==1):
                    nextvalue = pressurel[0]
                    if(nextvalue > firstvalue):
                        currentPressure = nextvalue
                    #    firstvalue = currentPressure
                    if(nextvalue < firstvalue):
                        currentPressure = firstvalue
                    firstvalue = currentPressure    
            if(a == 0):
                    firstvalue = pressurel[0]
                    print('firstvalue',firstvalue)
                    currentPressure = firstvalue
                    a = 1
            if (currentPressure < pressurel[0]):
                currentPressure = pressurel[0]
            else:
               currentPressure = firstvalue
            print('cp',currentPressure)
            self.dataDict["Dpress+"].append(currentPressure)   
        if (graph == 1):
            print('Exhaling')
            currentPressure = int(data[3])
            
            print('cp',currentPressure)
            self.dataDict["Dpress+"].append(currentPressure)
    
        if len(data) < 10:
            print("dropping data")
            return None
        #print(data)
        #self.dataDict["curr_act"] = int(data[0])
        '''
        self.dataDict["o2conc"].insert(0, int(data[1]))
        self.dataDict["AirV"].insert(0, int(data[2]))
        self.dataDict["Dpress+"].insert(0, int(data[3]))
        self.dataDict["Dpress-"].insert(0, int(data[4]))
        self.dataDict["press+"].insert(0, int(data[5]))
        self.dataDict["press-"].insert(0, int(data[6]))
        self.dataDict["co2"].insert(0, int(data[7]))
        self.dataDict["temp"].insert(0, int(data[8]))
        self.dataDict["hum"].insert(0, int(data[9]))
        '''

        self.dataDict["o2conc"].append(int(data[1]))
        self.dataDict["AirV"].append(int(data[2]))
        print('o2conc_airv')
        # # Simbu
#        pressure = []
  #      pressure.append(int(data[3]))
   #     currentpress = []
  #      currentpress.append(int(data[3])-580)
      #  CPressure = int(data[3])
        #print('pressure',currentPressure)
   #     print(pressure)
 #       with open('pressure.txt', 'w') as filehandle:
 #           for items in pressure:
 #               filehandle.write('%d \n' % items)
  #      with open('curentpressure.txt', 'w') as filehandle:
 #           for items in currentpress:
  #              filehandle.write('%d \n' % items)        
        # if(self.bthThread.breathStatus==1):
        #if(currentPressure > 0):

        #     else:
        #         self.dataDict["Dpress+"].append(dataDict["Dpress+"][-1])
        # else:
        #     self.dataDict["Dpress+"].append(currentPressure)
        # print("Simbu: currentVolData ", currentVolData)
    #    self.dataDict["Dpress+"].append(currentPressure)
        self.dataDict["Dpress-"].append(int(data[4]))
        self.dataDict["press+"].append(int(data[5]))
        self.dataDict["press-"].append(int(data[6]))
        self.dataDict["co2"].append(int(data[7]))
        self.dataDict["temp"].append(int(data[8]))
      #  self.dataDict["hum"].append(int(data[9]))

        if len(self.dataDict["o2conc"]) >200:
            self.dataDict["o2conc"].pop(0)
            self.dataDict["AirV"].pop(0)
            self.dataDict["Dpress+"].pop(0)
            self.dataDict["Dpress-"].pop(0)
            self.dataDict["press+"].pop(0)
            self.dataDict["press-"].pop(0)
            self.dataDict["co2"].pop(0)
            self.dataDict["temp"].pop(0)
            #self.dataDict["hum"].pop(0)
      
            
        
        return self.dataDict

    def run(self):
        # Do something...
        if self.firstLaunch :
            self.initSerData()
            self.firstLaunch=False
        #self.sendValues()
        print("starting thread")
        while self.running:
            data_m = self.getdata()
            if data_m != None:
                self.threadSignal.emit(data_m)

            QThread.msleep(10)
        #GPIO.output(4,GPIO.LOW)
        print("stopped thread")
        #self.threadSignal.emit(self.startParm)

class ControlPanel(QFrame):
    Vent_modes = ["None", "PRVC", "VC", "PC", "PS", "SIMV(VC)+PS", "SIMV(PC)+PS"]
    tid = []
    pressureDisplay = []
    ventMode = 0;
    priorityIdx = -1
    timesReachedLowPress = 0


    def __init__(self, parent):
        #super().__init__()
        QFrame.__init__(self)
        self.beThread = backendWorker("hello")
        self.beThread.threadSignal.connect(self.updateData)
        self.beThread.stopSignal.connect(self.beThread.stop)
        self.bthThread = breathWorker()
        self.bthThread.stopSignal.connect(self.bthThread.stop)
        self.readSettings()
        self.initUI()

        ###### graph enabler ##############
        self.pressureCanvasVisible = True
        self.o2CanvasVisible = True
        self.tidalCanvasVisible = True
        self.diffPressureVisible = True

    def readSettings(self):
        params = ["pressure", "volume", "bpm", "peep", "fio2"]
        # reading the data from the file
        with open('settings.txt') as f:
            data = f.read()

        print("Data type before reconstruction : ", type(data))

        # reconstructing the data as a dictionary
        self.settings = json.loads(data)
        #self.settings = {}
        print("Data type after reconstruction : ", type(self.settings))
        for param in params:
            try:
                self.settings[param]["min"]
                self.settings[param]["max"]
                self.settings[param]["default"]

            except KeyError as e:
                print('KeyError - missing key ["%s"]["%s"]' % (param, str(e)) )



    def onStart(self):
        print("pressed start button")
        dataFetched = self.fetchData()
        self.beThread.dataUpdate = dataFetched
        self.bthThread.updateData(dataFetched)
        self.beThread.running = True
        self.bthThread.running = True
        self.disableUI()
        self.beThread.start()
        self.bthThread.start()

    def onStop(self):
        print("pressed stop button")
        self.beThread.stopSignal.emit()
        self.bthThread.stopSignal.emit()
        self.enableUI()


    def translate(self, value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)


    def fetchData(self):
        dataFetched = {}
        pdata = int(self.translate(self.dsPh.tuner.value, self.settings["pressure"]["min"], self.settings["pressure"]["max"], 0, 100))
        voldata = int(self.translate(self.dsVol.tuner.value, self.settings["volume"]["min"], self.settings["volume"]["max"], 0, 100))
        soldata = pdata if ( self.priorityIdx == 0) else voldata
        print("soldata" + str(soldata))
        #soldata = max(pdata, voldata)
        #self.spinPh.setValue(int(self.translate(soldata, 0, 100, 0, 40)))
        self.dsPh.tuner.slide.setValue(int(self.translate(soldata, 0, 100, self.settings["pressure"]["min"], self.settings["pressure"]["max"])))
        self.dsPh.tuner.value = int(self.translate(soldata, 0, 100, self.settings["pressure"]["min"], self.settings["pressure"]["max"]))
        self.dsPh.button.setText(str(int(self.translate(soldata, 0, 100, self.settings["pressure"]["min"], self.settings["pressure"]["max"]))))
        #self.spinVol.setValue(int(self.translate(soldata, 0, 100, 20, 500)))
        self.dsVol.tuner.slide.setValue(int(self.translate(soldata, 0, 100, self.settings["volume"]["min"], self.settings["volume"]["max"])))
        self.dsVol.tuner.value = int(self.translate(soldata, 0, 100, self.settings["volume"]["min"], self.settings["volume"]["max"]))
        self.dsVol.button.setText(str(int(self.translate(soldata, 0, 100, self.settings["volume"]["min"], self.settings["volume"]["max"]))))
        print("range test : "+str(pdata)+" "+str(voldata)+" "+str(soldata))
        if self.ventMode=='VC':
            dataFetched["pressure"] = str(voldata)
        else:
            dataFetched["pressure"] = str(soldata)
        ## computing breathing intervals ##
        bpm = self.dsBpm.tuner.value
        ieRatio = self.comboIER.currentIndex() + 2
        breathCount = 60 / bpm
        self.rrdata.setText(str(self.dsBpm.tuner.value))

        inhaleTime = (breathCount/ieRatio) * 1000
        exhaleTime = (breathCount * 1000) - inhaleTime

        ################################################

        dataFetched["intime"] = inhaleTime
        dataFetched["outtime"] = exhaleTime
        self.bpmdata.setText(str(self.comboIER.currentText()))
        dataFetched["BPM"] = str(self.dsBpm.tuner.value)
        dataFetched["I:E"] = str(self.comboIER.currentText())
        dataFetched["peep"] = str(self.dsPeep.tuner.value)
        dataFetched["fio2"] = str(self.dsFio2.tuner.value)
        dataFetched["volume_tuner"] = str(self.dsVol.tuner.value)
        dataFetched["current_vol"] = str(random.randint(-10,20) + self.dsVol.tuner.value)

        return dataFetched

    def updateData(self, data):
        #print("recieved data = ", data)
        if data is None:
            return

        if self.bthThread.breathStatus == 0:
            #self.onLabel.setStyleSheet("QLabel {background-color: green; }")
            #onLabel.setMargin(20)
            #self.offLabel.setStyleSheet("QLabel {background-color: grey; }")
            self.activitydata.setText("INHALE")
            # self.pressureDisplay.append(self.dsPh.tuner.value)
            self.DpressPdata.setNum(self.dsPh.tuner.value)
            #self.tid.append(8)
            self.tidata.setText("8")
            self.pipdata.setText(str(self.dsPh.tuner.value))
            _volumeComputation = int(self.dsVol.tuner.value) + int(random.randint(-10,5))
            self.vedata.setText(str(_volumeComputation))
            self.peepdata.setText("-")

            # print("Inhale end")
        else:
            #self.onLabel.setStyleSheet("QLabel {background-color: grey; }") #onLabel.setMargin(20)
            #self.offLabel.setStyleSheet("QLabel {background-color: green; }")
            self.activitydata.setText("EXHALE")
            self.pressureDisplay.append(self.dsPh.tuner.value * -1)
            self.DpressPdata.setNum(0)
            #self.tid.append(0)
            self.tidata.setText("-")
            _volumeComputation = int(self.dsPeep.tuner.value) + int(random.randint(-1,2))
            self.vedata.setText(str(_volumeComputation))
            self.pipdata.setText(str(self.dsPh.tuner.value))
            self.peepdata.setText(str(self.dsPeep.tuner.value))

            ##### detect low pressure and stop exhale ######
            ################################################
            # _trigger = 3 * (int(self.comboTRI.currentText()))
            #
            # if (data["Dpress+"][-1] < _trigger):
            #     print("low pressure detected : " + str(self.timesReachedLowPress))
            #     if(self.bthThread.breathStatus==0):
            #         print("low pressure !!!!  during inhalation")
            #     else:
            #         self.timesReachedLowPress = self.timesReachedLowPress + 1
            #         if(self.timesReachedLowPress>3):
            #            self.bthThread._exhale_event.set()
            #            print("low pressure !!!! exhale event stopped")
            #            self.bthThread._exhale_event.clear()

            # timesReachedLowPress = 0



        if (len(self.tid) >120):
            self.tid.pop(0)
            # print("popping")
        #print(self.tid)

        # self.o2concdata.setNum(data["o2conc"][-1])
        oxyValue = round((data["o2conc"][-1]),0)
        oxyDisplay = 21;
        if oxyValue>21:
            oxyDisplay = oxyValue
        else:
            oxyDisplay = 21;
        self.o2concdata.setNum(data["o2conc"][-1])
        self.airVeldata.setNum(data["Dpress+"][-1])
        # self.DpressPdata.setNum(data["Dpress+"][-1])
        # pressPdata
        self.DpressNdata.setNum(500)
        self.DpressNdata.setNum(data["Dpress-"][-1])
        self.pressPdata.setNum(data["Dpress+"][-1])
        self.pressNdata.setNum(data["press-"][-1])
        self.co2data.setNum(data["co2"][-1])
        self.tempdata.setNum(data["temp"][-1])
        #self.humdata.setNum(data["hum"][-1])

        #### Graph update#####
        ######################
        if self.pressureCanvasVisible:
            self.pressure_data_line.setData(data["Dpress+"][:180])
            # self.pressure_data_line.setData(self.pressureDisplay[:100])
        if self.o2CanvasVisible:
            self.o2_data_line.setData(data["o2conc"][:180])
        if self.tidalCanvasVisible:
            self.tidal_data_line.setData(self.tid[:100])
        if self.diffPressureVisible:
            # self.diffPressure_data_line.setData(data["press+"][:100])
            self.diffPressure_data_line.setData(self.pressureDisplay[:100])


    def initUI(self):

        self.setStyleSheet("QSpinBox { border: 3px solid blue; border-radius: 5px; background-color: gray; }"
            "QSpinBox::up-button { subcontrol-position: center left; width: 25px; height: 25px;}"
            "QSpinBox::down-button { subcontrol-position: center right; width: 25px; height: 25px; }")

        '''
        self.setStyleSheet("QSpinBox { border: 3px solid red; border-radius: 5px; background-color: yellow; }"
            "QSpinBox::up-arrow { border-left: 17px solid none;"
            "border-right: 17px solid none; border-bottom: 17px solid black; width: 0px; height: 0px; }"
            "QSpinBox::up-arrow:hover { border-left: 17px solid none;"
            "border-right: 17px solid none; border-bottom: 17px solid black; width: 0px; height: 0px; }"
            "QSpinBox::up-button { subcontrol-position: center left; width: 40px; height: 37px; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0.25 #aaaaaa, stop: 1 #888888) }"
            "QSpinBox::up-button:hover { width: 40px; height: 37px; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0.25 #aaaaaa, stop: 1 #888888) }"
            "QSpinBox::down-arrow { border-left: 17px solid none;"
            "border-right: 17px solid none; border-top: 17px solid black; width: 0px; height: 0px; }"
            "QSpinBox::down-arrow:hover { border-left: 17px solid none;"
            "border-right: 17px solid none; border-top: 17px solid black; width: 0px; height: 0px; }"
            "QSpinBox::down-button { subcontrol-position: center right; width: 40px; height: 37px; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0.25 #aaaaaa, stop: 1 #888888) }"
            "QSpinBox::down-button:hover { width: 40px; height: 37px; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0.25 #aaaaaa, stop: 1 #888888) }")
        '''
        self.startButton = QPushButton("START", self)
        self.startButton.clicked.connect(self.onStart)
        self.stopButton = QPushButton("STOP", self)
        self.stopButton.clicked.connect(self.onStop)

        self.stopButton.setVisible(False)

        self.hbox = QHBoxLayout()

        #grid = QGridLayout()

        #grid.addWidget()

        #hbox.addStretch(1)
        self.hbox.addWidget(self.startButton)
        self.hbox.addWidget(self.stopButton)

        self.btSpacer = QSpacerItem(100, 30)

        """spinbox design"""

        #self.setStyleSheet("""QSpinBox { padding-right: 15px; padding-left: 15px; border-image: url(:/images/frame.png) 4; border-width: 3;}
        #                        QSpinBox::up-button{subcontrol-origin: margin; subcontrol-position: center right; width: 16px; border-image: url(:/images/spinup.png) 1; border-width: 1px;}
        #                        QSpinBox::up-button:hover { border-image: url(:/images/spinup_hover.png) 1;}
        #                        QSpinBox::up-button:pressed {border-image: url(:/images/spinup_pressed.png) 1;}
        #                        QSpinBox::up-arrow { image: url(:/images/up_arrow.png); width: 7px; height: 7px;}
        #                        QSpinBox::down-button { subcontrol-origin: margin; subcontrol-position: center left; width: 16px; border-width: 1px;} """)


        self.noCB = -1
        """ pressure button """
        '''
        self.phLabel = QLabel('Set Pressure', self)
        self.spinPh = QSpinBox(self)
        self.spinPh.setRange(0, 40)
        self.spinPh.setSuffix(" cmH2O")
        self.font = self.spinPh.font()
        self.font.setPointSize(10)
        self.spinPh.setFont(self.font)
        #self.spinPh.setStyleSheet("QSpinBox {background-color: #F8F8FF;}")

        self.vboxPh = QVBoxLayout()
        self.vboxPh.addStretch(1)
        self.vboxPh.addWidget(self.phLabel)
        self.vboxPh.addWidget(self.spinPh)
        self.phWidget = QFrame()
        self.phWidget.setLayout(self.vboxPh)
        '''
        self.tuner1 = Tuner("pressure", Range=[self.settings["pressure"]["min"],self.settings["pressure"]["max"],1], default=self.settings["pressure"]["default"])
        self.b1 = QPushButton(str(self.settings["pressure"]["default"]))
        self.b1.setStyleSheet ('QPushButton:checked {background-color: yellow;border: none;}')
        self.b1.setFont(QFont('Times', 30))

        self.phLabel = QLabel('Pressure')
        #self.phLabel.setStyleSheet("QLabel { background-color : white; color : black; }")
        #self.b1.resize(50, 50)
        self.b1.setCheckable(True)
        self.b1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.dsPh = dataStack(name="cmH2O", index = 0, dial=self.tuner1, button=self.b1, obj=self)
        self.b1.clicked.connect(lambda:self.whichbtn(0))

        self.vboxPh = QVBoxLayout()
        #self.vboxPh.addStretch(1)
        self.vboxPh.addWidget(self.phLabel)
        self.vboxPh.addWidget(self.b1)

        """ Volume Button """
        '''
        self.volLabel = QLabel('Set Volume', self)
        self.spinVol = QSpinBox(self)
        self.spinVol.setRange(20, 500)
        self.font = self.spinVol.font()
        self.font.setPointSize(10)
        self.spinVol.setFont(self.font)
        #self.spinPh.setStyleSheet("QSpinBox {background-color: #F8F8FF;}")

        self.vboxVol = QVBoxLayout()
        self.vboxVol.addStretch(1)
        self.vboxVol.addWidget(self.volLabel)
        self.vboxVol.addWidget(self.spinVol)

        self.volWidget = QFrame()
        self.volWidget.setLayout(self.vboxVol)
        '''
        self.tuner2 = Tuner("Volume", Range=[self.settings["volume"]["min"], self.settings["volume"]["max"],1], default=self.settings["volume"]["default"])
        self.b2 = QPushButton(str(self.settings["volume"]["default"]))
        self.b2.setStyleSheet ('QPushButton:checked {background-color: yellow;border: none;}')
        self.b2.setFont(QFont('Times', 30))

        self.volLabel = QLabel('Vol')
        self.volLabel.adjustSize()
        #self.volLabel.setStyleSheet("QLabel { background-color : white; color : white; }")
        #self.b1.resize(50, 50)
        self.b2.setCheckable(True)
        self.b2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.dsVol = dataStack(name="vol", index = 1, dial=self.tuner2, button=self.b2, obj=self)
        self.b2.clicked.connect(lambda:self.whichbtn(1))

        self.vboxVol = QVBoxLayout()
        #self.vboxVol.addStretch(1)
        self.vboxVol.addWidget(self.volLabel)
        self.vboxVol.addWidget(self.b2)

        # self.volWidget = QFrame()
        # self.volWidget.setLayout(self.vboxVol)
        # self.volWidget.setFrameStyle(QFrame.Panel | QFrame.Raised);
        # self.volWidget.setLineWidth(3);
        # self.volWidget.setMidLineWidth(3);


        """ No of Breath per minute """
        '''
        self.bpmLabel = QLabel('No. of breaths (per minute)', self)
        self.spinBPM = QSpinBox(self)
        self.spinBPM.setRange(12, 20)
        self.spinBPM.setSuffix(" BPM")
        font = self.spinBPM.font()
        font.setPointSize(10)
        self.spinBPM.setFont(font)

        self.vboxBPM = QVBoxLayout()
        self.vboxBPM.addStretch(1)
        self.vboxBPM.addWidget(self.bpmLabel)
        self.vboxBPM.addWidget(self.spinBPM)

        self.bpmWidget = QFrame()
        self.bpmWidget.setLayout(self.vboxBPM)
        '''
        self.tuner3 = Tuner("breaths per min", Range=[self.settings["bpm"]["min"],self.settings["bpm"]["max"],1], default=self.settings["bpm"]["default"])
        self.b3 = QPushButton(str(self.settings["bpm"]["default"]))
        self.b3.setStyleSheet ('QPushButton:checked {background-color: yellow;border: none;}')
        self.b3.setFont(QFont('Times', 30))

        self.bpmLabel = QLabel('BPM')
        #self.bpmLabel.setStyleSheet("QLabel { background-color : white; color : black; }")
        #self.b1.resize(50, 50)
        self.b3.setCheckable(True)
        self.b3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.dsBpm = dataStack(name="BPM", index = 2, dial=self.tuner3, button=self.b3, obj=self)
        self.b3.clicked.connect(lambda:self.whichbtn(2))

        self.vboxBPM = QVBoxLayout()
        #self.vboxBPM.addStretch(1)
        self.vboxBPM.addWidget(self.bpmLabel)
        self.vboxBPM.addWidget(self.b3)

        """ Peep """
        '''
        self.peepLabel = QLabel('Peep', self)
        self.spinPeep = QSpinBox(self)
        self.spinPeep.setRange(0, 40)
        self.spinPeep.setSuffix(" cmH2O")
        font = self.spinPeep.font()
        font.setPointSize(10)
        self.spinPeep.setFont(font)

        self.vboxPeep = QVBoxLayout()
        self.vboxPeep.addStretch(1)
        self.vboxPeep.addWidget(self.peepLabel)
        self.vboxPeep.addWidget(self.spinPeep)

        self.peepWidget = QFrame()
        self.peepWidget.setLayout(self.vboxPeep)
        '''
        self.tuner4 = Tuner("PEEP", Range=[self.settings["peep"]["min"],self.settings["peep"]["max"],1], default=self.settings["peep"]["default"])
        self.b4 = QPushButton(str(self.settings["peep"]["default"]))
        self.b4.setStyleSheet ('QPushButton:checked {background-color: yellow;border: none;}')
        self.b4.setFont(QFont('Times', 40))

        self.peepLabel = QLabel('PEEP')
        #self.peepLabel.setStyleSheet("QLabel { background-color : white; color : black; }")
        #self.b1.resize(50, 50)
        self.b4.setCheckable(True)
        self.b4.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.dsPeep = dataStack(name="PEEP", index = 3, dial=self.tuner4, button=self.b4, obj=self)
        self.b4.clicked.connect(lambda:self.whichbtn(3))

        self.vboxPeep = QVBoxLayout()
        #self.vboxPeep.addStretch(1)
        self.vboxPeep.addWidget(self.peepLabel)
        self.vboxPeep.addWidget(self.b4)

        """ FiO2 """
        '''
        self.fio2Label = QLabel('FiO2', self)
        self.spinFio2 = QSpinBox(self)
        self.spinFio2.setRange(21, 100)
        self.spinFio2.setSuffix(" %")
        font = self.spinFio2.font()
        font.setPointSize(10)
        self.spinFio2.setFont(font)

        self.vboxFio2 = QVBoxLayout()
        self.vboxFio2.addStretch(1)
        self.vboxFio2.addWidget(self.fio2Label)
        self.vboxFio2.addWidget(self.spinFio2)

        self.fio2Widget = QFrame()
        self.fio2Widget.setLayout(self.vboxFio2)
        '''
        self.tuner5 = Tuner("FiO2", Range=[self.settings["fio2"]["min"],self.settings["fio2"]["max"],1], default=self.settings["fio2"]["default"])
        self.b5 = QPushButton(str(self.settings["fio2"]["default"]))
        self.b5.setStyleSheet ('QPushButton:checked {background-color: yellow;border: none;}')
        self.b5.setFont(QFont('Times', 40))

        self.fio2Label = QLabel('FiO2')
        #self.fio2Label.setStyleSheet("QLabel { background-color : white; color : black; }")
        #self.b1.resize(50, 50)
        self.b5.setCheckable(True)
        self.b5.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.dsFio2 = dataStack(name="FiO2", index = 4, dial=self.tuner5, button=self.b5, obj=self)
        self.b5.clicked.connect(lambda:self.whichbtn(4))

        self.vboxFio2 = QVBoxLayout()
        #self.vboxFio2.addStretch(1)
        self.vboxFio2.addWidget(self.fio2Label)
        self.vboxFio2.addWidget(self.b5)


        self.dsList = [self.dsPh, self.dsVol, self.dsBpm, self.dsPeep, self.dsFio2]


        """ Inhale and exhale ratio """
        self.ierLabel = QLabel('I:E', self)
        self.comboIER = QComboBox(self)
        self.comboIER.addItem("1:1")
        self.comboIER.addItem("1:2")
        self.comboIER.addItem("1:3")
        self.comboIER.addItem("1:4")

        font = self.comboIER.font()
        font.setPointSize(30)
        self.comboIER.setFont(font)
        self.comboIER.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.vboxIER = QVBoxLayout()
        #self.vboxIER.addStretch(1)
        self.vboxIER.addWidget(self.ierLabel)
        self.vboxIER.addWidget(self.comboIER)


        """ Trigger """
        self.triLabel = QLabel('Trigger', self)
        self.comboTRI = QComboBox(self)
        self.comboTRI.addItem("-10")
        self.comboTRI.addItem("-9")
        self.comboTRI.addItem("-8")
        self.comboTRI.addItem("-7")
        self.comboTRI.addItem("-6")
        self.comboTRI.addItem("-5")
        self.comboTRI.addItem("-4")
        self.comboTRI.addItem("-3")

        font = self.comboTRI.font()
        font.setPointSize(30)
        self.comboTRI.setFont(font)
        self.comboTRI.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.vboxTRI = QVBoxLayout()
        #self.vboxIER.addStretch(1)
        self.vboxTRI.addWidget(self.triLabel)
        self.vboxTRI.addWidget(self.comboTRI)

        # self.ierWidget = QFrame()
        # self.ierWidget.setLayout(self.vboxIER)
        # self.ierWidget.setFrameStyle(QFrame.Panel | QFrame.Raised);
        # self.ierWidget.setLineWidth(3);
        # self.ierWidget.setMidLineWidth(3);

        """ Ventilation modes """
        self.vmLabel = QLabel('Ventilation Modes', self)
        self.comboVM = QComboBox(self)
        self.comboVM.addItems(self.Vent_modes)

        font = self.comboVM.font()
        font.setPointSize(10)
        self.comboVM.setFont(font)
        self.comboVM.setStyleSheet('background-color: #000000;color: #FFFFFF')

        self.vboxVM = QVBoxLayout()
        self.vboxVM.addStretch(1)
        self.vboxVM.addWidget(self.vmLabel)
        self.vboxVM.addWidget(self.comboVM)

        self.comboVM.currentIndexChanged.connect(self.on_currentIndexChanged)

        self.vmWidget = QFrame()
        self.vmWidget.setLayout(self.vboxVM)

        #spinFio2.setDisabled(True)


        controlgrid = QGridLayout()
        controlgrid.addLayout(self.vboxPh, 0, 0)
        controlgrid.addLayout(self.vboxVol, 0, 1)
        controlgrid.addLayout(self.vboxBPM, 0, 2)
        controlgrid.addLayout(self.vboxPeep, 0, 3)
        controlgrid.addLayout(self.vboxFio2, 0, 4)
        controlgrid.addLayout(self.vboxIER, 0, 5)
        controlgrid.addLayout(self.vboxTRI, 0, 6)

        tunerBox = QVBoxLayout()

        tunerBox.addWidget(self.tuner1)
        tunerBox.addWidget(self.tuner2)
        tunerBox.addWidget(self.tuner3)
        tunerBox.addWidget(self.tuner4)
        tunerBox.addWidget(self.tuner5)

        self.tunerFrame=QFrame()
        self.tunerFrame.setLayout(tunerBox)
        self.tunerFrame.setFrameStyle(QFrame.Panel | QFrame.Sunken);
        self.tunerFrame.setLineWidth(3);
        self.tunerFrame.setMidLineWidth(3);
        self.tunerFrame.setVisible(False)
        #tunerFrame.setStyleSheet("min-width: 80px; min-height: 80px;")


        """ compression status """
        '''
        self.compressLabel = QLabel("compression :", self)
        self.compressLabel.setFont(self.compressLabel.font().setPointSize(14))
        self.onLabel = QLabel("ON", self)
        self.onLabel.setFixedSize(50, 50)
        self.offLabel = QLabel("OFF", self)
        self.offLabel.setFixedSize(50, 50)
        self.onLabel.setAlignment(Qt.AlignCenter)
        self.offLabel.setAlignment(Qt.AlignCenter)


        #self.cmpSpacer1 = QSpacerItem(25, 50)
        self.cmpSpacer2 = QSpacerItem(50, 50)
        self.compressionHbox = QGridLayout()
        self.compressionHbox.addWidget(self.compressLabel, 0,1)
        self.compressionHbox.addWidget(self.onLabel, 0,2)
        #self.compressionHbox.addItem(self.cmpSpacer1, 0,3)
        self.compressionHbox.addWidget(self.offLabel, 0,4)
        self.compressionHbox.addItem(self.cmpSpacer2, 0,5)


        self.onLabel.setStyleSheet("QLabel {background-color: grey; }")
        #onLabel.setMargin(20)
        self.offLabel.setStyleSheet("QLabel {background-color: grey; }")
        '''

        #### update button ###########
        self.updateButton = QPushButton("UPDATE")
        self.updateButton.clicked.connect(self.onUpdate)
        self.updateButton.setVisible(False)




        #########################################################################
        ###################### data update view #################################
        #########################################################################

        '''
        self.dataviewlabel = QLabel('Graph view', self)
        self.dataviewlabel.setStyleSheet("QLabel {background-color: #fafad2;}")
        self.dataviewlabel.setAlignment(Qt.AlignCenter)
        '''

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(255, 255, 255))

        #fig = Figure( dpi=72, facecolor=(0.8,.80,.80), edgecolor=(1,1,1))
        #self.ax = fig.add_subplot(111)
        #self.ax.set_facecolor('lightgrey')
        #ax.plot([0,1,5, 2, 7, 2, 5, 1, 3,8 ,4], '-o')
        """
        self.pressureCanvas = MplCanvas(self, dpi=72, facecolor=(0.337,.364,.439), edgecolor=(0,0,0)) #FigureCanvas(fig)
        self.o2Canvas = MplCanvas(self, dpi=72, facecolor=(0.337,.364,.439), edgecolor=(0,0,0))
        self.tidalCanvas = MplCanvas(self, dpi=72, facecolor=(0.337,.364,.439), edgecolor=(0,0,0))
        self.diffPressureCanvas = MplCanvas(self, dpi=72, facecolor=(0.337,.364,.439), edgecolor=(0,0,0))
        """

        self.pressureCanvas = pg.PlotWidget()
        self.o2Canvas = pg.PlotWidget()
        self.tidalCanvas = pg.PlotWidget()
        self.diffPressureCanvas = pg.PlotWidget()

        self.pressureCanvas.setBackground(0.1)
        self.o2Canvas.setBackground(0.1)
        self.tidalCanvas.setBackground(0.1)
        self.diffPressureCanvas.setBackground(0.1)

        self.pressureCanvas.getPlotItem().hideAxis('bottom')
        self.o2Canvas.getPlotItem().hideAxis('bottom')
        self.tidalCanvas.getPlotItem().hideAxis('bottom')
        self.diffPressureCanvas.getPlotItem().hideAxis('bottom')

        self.y1 = [0] #[randint(-20,20) for _ in range(50)]
        self.y2 = [0] #[randint(-20,20) for _ in range(50)]
        self.y3 = [0] #[randint(-20,20) for _ in range(50)]
        self.y4 = [0] #[randint(-20,20) for _ in range(50)]

        self.pressure_data_line =  self.pressureCanvas.plot(self.y1, fillLevel=0, brush=(150,50,150,50))
        self.o2_data_line =  self.o2Canvas.plot(self.y2, fillLevel=0, brush=(50,150,50,50))
        self.tidal_data_line =  self.tidalCanvas.plot(self.y3, fillLevel=0, brush=(150,50,50,50))
        self.diffPressure_data_line =  self.diffPressureCanvas.plot(self.y4, fillLevel=0, brush=(50,150,150,50))


        ###### Breath ratio ######

        self.bpmdatalabel = QLabel('Breath ratio', self)
        self.bpmdatalabel.setAlignment(Qt.AlignCenter)
        self.bpmdata = QLabel('1:1', self)

        self.bpmdata.setAlignment(Qt.AlignCenter)
        self.bpmdata.setFont(QFont('Arial', 50))
        #self.bpmdata.setStyleSheet("border : 2px solid black; background-color: #ddddeb;")
        #self.bpmdata.setStyleSheet("box-shadow:20px 20px 20px 10px red;")
        #self.bpmdata.setGraphicsEffect(shadow)
        self.bpmdataVbox = QVBoxLayout()
        self.bpmdataVbox.addWidget(self.bpmdatalabel, 1)
        self.bpmdataVbox.addWidget(self.bpmdata, 3)

        '''
        ############## Widget container class ##############
        ################### test ######################
        self.bpmDataWidget = qwidgetContainer(QLabel('Breath ratio'), QLabel('1:1'), self)
        self.bpmDataWidget.widget1.setAlignment(Qt.AlignCenter)
        self.bpmDataWidget.widget2.setAlignment(Qt.AlignCenter)
        self.bpmDataWidget.widget2.setFont(self.bpmDataWidget.widget1.font().setPointSize(30))
        #self.bpmDataWidget.testWidget.setGraphicsEffect(shadow)
        #self.bpmDataWidget.setStyleSheet("background-color: grey;")
        '''

        ###### Current activity ######
        self.activitydatalabel = QLabel('Current Activity', self)
        self.activitydatalabel.setAlignment(Qt.AlignCenter)
        self.activitydata = QLabel('INHALE', self)
        self.activitydata.setAlignment(Qt.AlignCenter)

        self.activitydata.setFont(QFont('Arial', 20))
        #self.activitydata.setStyleSheet("border : 2px solid black")
        self.activitydataVbox = QVBoxLayout()
        self.activitydataVbox.addWidget(self.activitydatalabel, 1)
        self.activitydataVbox.addWidget(self.activitydata, 3)

        ###### PIP ######
        self.pipdatalabel = QLabel('PIP', self)
        self.pipdatalabel.setAlignment(Qt.AlignCenter)
        self.pipdata = QLabel('-', self)
        self.pipdata.setAlignment(Qt.AlignCenter)

        self.pipdata.setFont(QFont('Arial', 50))
        self.pipdataVbox = QVBoxLayout()
        self.pipdataVbox.addWidget(self.pipdatalabel, 1)
        self.pipdataVbox.addWidget(self.pipdata, 3)

        ###### Ve ######
        self.vedatalabel = QLabel('Ve', self)
        self.vedatalabel.setAlignment(Qt.AlignCenter)
        self.vedata = QLabel('-', self)
        self.vedata.setAlignment(Qt.AlignCenter)

        self.vedata.setFont(QFont('Arial', 50))
        self.vedataVbox = QVBoxLayout()
        self.vedataVbox.addWidget(self.vedatalabel, 1)
        self.vedataVbox.addWidget(self.vedata, 3)

        ###### P Mean ######
        self.pmeandatalabel = QLabel('P mean', self)
        self.pmeandatalabel.setAlignment(Qt.AlignCenter)
        self.pmeandata = QLabel('-', self)
        self.pmeandata.setAlignment(Qt.AlignCenter)

        self.pmeandata.setFont(QFont('Arial', 50))
        self.pmeandataVbox = QVBoxLayout()
        self.pmeandataVbox.addWidget(self.pmeandatalabel, 1)
        self.pmeandataVbox.addWidget(self.pmeandata, 3)

        ###### Respiratory Rate ######
        self.rrdatalabel = QLabel('RR', self)
        self.rrdatalabel.setAlignment(Qt.AlignCenter)
        self.rrdata = QLabel('-', self)
        self.rrdata.setAlignment(Qt.AlignCenter)

        self.rrdata.setFont(QFont('Arial', 50))
        self.rrdataVbox = QVBoxLayout()
        self.rrdataVbox.addWidget(self.rrdatalabel, 1)
        self.rrdataVbox.addWidget(self.rrdata, 3)

        ###### Tidel ######
        self.tidatalabel = QLabel('Ti', self)
        self.tidatalabel.setAlignment(Qt.AlignCenter)
        self.tidata = QLabel('-', self)
        self.tidata.setAlignment(Qt.AlignCenter)

        self.tidata.setFont(QFont('Arial', 50))
        self.tidataVbox = QVBoxLayout()
        self.tidataVbox.addWidget(self.tidatalabel, 1)
        self.tidataVbox.addWidget(self.tidata, 3)

        ###### PEEP ######
        self.peepdatalabel = QLabel('PEEP', self)
        self.peepdatalabel.setAlignment(Qt.AlignCenter)
        self.peepdata = QLabel('-', self)
        self.peepdata.setAlignment(Qt.AlignCenter)

        self.peepdata.setFont(QFont('Arial', 50))
        self.peepdataVbox = QVBoxLayout()
        self.peepdataVbox.addWidget(self.peepdatalabel, 1)
        self.peepdataVbox.addWidget(self.peepdata, 3)


        ###### O2 concentration ######
        self.o2concdatalabel = QLabel('O2 Conc', self)
        self.o2concdatalabel.setAlignment(Qt.AlignCenter)
        self.o2concdata = QLabel('100', self)
        self.o2concdata.setAlignment(Qt.AlignCenter)

        self.o2concdata.setFont(QFont('Arial', 50))
        self.o2concdataVbox = QVBoxLayout()
        self.o2concdataVbox.addWidget(self.o2concdatalabel, 1)
        self.o2concdataVbox.addWidget(self.o2concdata, 3)

        ###### Peep value ######
        self.airVeldatalabel = QLabel('Air Velocity', self)
        self.airVeldatalabel.setAlignment(Qt.AlignCenter)
        self.airVeldata = QLabel('4', self)
        self.airVeldata.setAlignment(Qt.AlignCenter)

        self.airVeldata.setFont(self.airVeldata.font().setPointSize(30))
        self.airVeldataVbox = QVBoxLayout()
        self.airVeldataVbox.addWidget(self.airVeldatalabel, 1)
        self.airVeldataVbox.addWidget(self.airVeldata, 3)

        ###### Respiratory rate ######
        self.DpressPdatalabel = QLabel('Pressure D+', self)
        self.DpressPdatalabel.setAlignment(Qt.AlignCenter)
        self.DpressPdata = QLabel('12', self)
        self.DpressPdata.setAlignment(Qt.AlignCenter)

        self.DpressPdata.setFont(QFont('Arial', 50))
        self.DpressPdata.setNum(100)
        self.DpressPdataVbox = QVBoxLayout()
        self.DpressPdataVbox.addWidget(self.DpressPdatalabel, 1)
        self.DpressPdataVbox.addWidget(self.DpressPdata, 3)

        ###### V-MAX ######
        self.DpressNdatalabel = QLabel('Pressure D-', self)
        self.DpressNdatalabel.setAlignment(Qt.AlignCenter)
        self.DpressNdata = QLabel('1.1', self)
        self.DpressNdata.setAlignment(Qt.AlignCenter)

        self.DpressNdata.setFont(self.DpressNdata.font().setPointSize(30))
        self.DpressNdataVbox = QVBoxLayout()
        self.DpressNdataVbox.addWidget(self.DpressNdatalabel, 1)
        self.DpressNdataVbox.addWidget(self.DpressNdata, 3)

        ###### Pressure ######
        self.pressPdatalabel = QLabel('+ve (cmH2O)', self)
        self.pressPdatalabel.setAlignment(Qt.AlignCenter)
        self.pressPdata = QLabel('25', self)
        self.pressPdata.setAlignment(Qt.AlignCenter)

        self.pressPdata.setFont(QFont('Arial', 50))
        self.pressPdataVbox = QVBoxLayout()
        self.pressPdataVbox.addWidget(self.pressPdatalabel, 1)
        self.pressPdataVbox.addWidget(self.pressPdata, 3)

        ###### Pressure ######
        self.pressNdatalabel = QLabel('-ve (cmH2O)', self)
        self.pressNdatalabel.setAlignment(Qt.AlignCenter)
        self.pressNdata = QLabel('25', self)
        self.pressNdata.setAlignment(Qt.AlignCenter)

        self.pressNdata.setFont(self.pressNdata.font().setPointSize(30))
        self.pressNdataVbox = QVBoxLayout()
        self.pressNdataVbox.addWidget(self.pressNdatalabel, 1)
        self.pressNdataVbox.addWidget(self.pressNdata, 3)

        ###### Co2 Concentration ######
        self.co2datalabel = QLabel('CO2 Conc', self)
        self.co2datalabel.setAlignment(Qt.AlignCenter)
        self.co2data = QLabel('25', self)
        self.co2data.setAlignment(Qt.AlignCenter)

        self.co2data.setFont(self.co2data.font().setPointSize(30))
        self.co2dataVbox = QVBoxLayout()
        self.co2dataVbox.addWidget(self.co2datalabel, 1)
        self.co2dataVbox.addWidget(self.co2data, 3)

        ###### Temperature ######
        self.tempdatalabel = QLabel('Temperature', self)
        self.tempdatalabel.setAlignment(Qt.AlignCenter)
        self.tempdata = QLabel('25', self)
        self.tempdata.setAlignment(Qt.AlignCenter)

        self.tempdata.setFont(self.tempdata.font().setPointSize(30))
        self.tempdataVbox = QVBoxLayout()
        self.tempdataVbox.addWidget(self.tempdatalabel, 1)
        self.tempdataVbox.addWidget(self.tempdata, 3)

        ###### Humidity ######
        self.humdatalabel = QLabel('Humidity', self)
        self.humdatalabel.setAlignment(Qt.AlignCenter)
        self.humdata = QLabel('25', self)
        self.humdata.setAlignment(Qt.AlignCenter)

        self.humdata.setFont(self.humdata.font().setPointSize(30))
        self.humdataVbox = QVBoxLayout()
        self.humdataVbox.addWidget(self.humdatalabel, 1)
        self.humdataVbox.addWidget(self.humdata, 3)

        ###### Tidal Volume ######
        self.tidalvoldatalabel = QLabel('Tidal (ml/kg)', self)
        self.tidalvoldatalabel.setAlignment(Qt.AlignCenter)
        self.tidalvoldata = QLabel('8', self)
        self.tidalvoldata.setAlignment(Qt.AlignCenter)

        self.tidalvoldata.setFont(QFont('Arial', 50))
        self.tidalvoldataVbox = QVBoxLayout()
        self.tidalvoldataVbox.addWidget(self.tidalvoldatalabel, 1)
        self.tidalvoldataVbox.addWidget(self.tidalvoldata, 3)

        self.rtGridbox = QGridLayout()
        print(self.rtGridbox.parent())
        self.rtGridbox.addLayout(self.bpmdataVbox, 1, 1)
        self.rtGridbox.addLayout(self.activitydataVbox, 1, 2)
        self.rtGridbox.addLayout(self.pipdataVbox, 2, 1)
        self.rtGridbox.addLayout(self.vedataVbox, 2, 2)
        self.rtGridbox.addLayout(self.pmeandataVbox, 3, 1)
        self.rtGridbox.addLayout(self.rrdataVbox, 3, 2)
        self.rtGridbox.addLayout(self.tidataVbox, 4, 1)
        self.rtGridbox.addLayout(self.peepdataVbox, 4, 2)
        # self.rtGridbox.addLayout(self.vedataVbox, 2, 2)
        #self.rtGridbox.addLayout(self.o2concdataVbox, 1, 3)
        # self.rtGridbox.addLayout(self.airVeldataVbox, 2, 1)
        #self.rtGridbox.addLayout(self.DpressPdataVbox, 2, 1)
        # self.rtGridbox.addLayout(self.DpressNdataVbox, 2, 2)
        #self.rtGridbox.addLayout(self.pressPdataVbox, 2, 3)
        # self.rtGridbox.addLayout(self.pressNdataVbox, 3, 1)
        #self.rtGridbox.addLayout(self.tidalvoldataVbox, 3, 1)
        # self.rtGridbox.addLayout(self.co2dataVbox, 3, 2)
        # self.rtGridbox.addLayout(self.tempdataVbox, 4, 1)
        # self.rtGridbox.addLayout(self.humdataVbox, 4, 2)

        self.rtGridFrame=QFrame()
        self.rtGridFrame.setLayout(self.rtGridbox)

        graphHolder = QVBoxLayout()
        graphdataHolder = QVBoxLayout()

        #pressureGraphHolder = QHBoxLayout()
        graphdataHolder.addLayout(self.pressPdataVbox)
        graphHolder.addWidget(self.pressureCanvas)

        #o2GraphHolder = QHBoxLayout()
        graphdataHolder.addLayout(self.o2concdataVbox)
        graphHolder.addWidget(self.o2Canvas)

        #tidalGraphHolder = QHBoxLayout()
        graphdataHolder.addLayout(self.tidalvoldataVbox)
        graphHolder.addWidget(self.tidalCanvas)

        #diffPressureGraphHolder = QHBoxLayout()
        graphdataHolder.addLayout(self.DpressPdataVbox)
        graphHolder.addWidget(self.diffPressureCanvas)

        graphview = QHBoxLayout()
        graphview.addLayout(graphHolder, 8)
        graphview.addLayout(graphdataHolder, 2)
        '''
        graphHolder.addLayout(pressureGraphHolder)
        graphHolder.addLayout(o2GraphHolder)
        graphHolder.addLayout(tidalGraphHolder)
        graphHolder.addLayout(diffPressureGraphHolder)
        '''

        ######### STATUS INDICATOR ###############
        #self.statusInd = QPushButton("", self)
        #self.statusInd.setStyleSheet("QPushButton {background-color: green; }")

        ##### graph view ##############
        #self.graphStack1 = QStackedWidget(self)
        #self.graphStack2 = QStackedWidget(self)
        '''
        self.graphStack1.addWidget(self.pressureCanvas)
        self.graphStack1.addWidget(self.diffPressureCanvas)
        self.graphStack1.addWidget(self.o2Canvas)
        self.graphStack1.addWidget(self.tidalCanvas)
        self.graphStack1.setCurrentIndex(0)


        self.graphStack2.addWidget(self.pressureCanvas)
        self.graphStack2.addWidget(self.diffPressureCanvas)
        self.graphStack2.addWidget(self.o2Canvas)
        self.graphStack2.addWidget(self.tidalCanvas)
        self.graphStack2.setCurrentIndex(2)
        '''
        '''
        self.combo1 = QComboBox()
        self.combo2 = QComboBox()

        self.combo1.addItem("Pressure")
        self.combo1.addItem("Diff Pressure")
        self.combo1.addItem("O2 Conc")
        self.combo1.addItem("Tidal Vol")
        self.combo1.currentIndexChanged.connect(self.btnstate1)

        self.combo2.addItem("Pressure")
        self.combo2.addItem("Diff Pressure")
        self.combo2.addItem("O2 Conc")
        self.combo2.addItem("Tidal Vol")
        self.combo2.currentIndexChanged.connect(self.btnstate2)
        '''

        '''
        self.pressureRadio = QRadioButton("pressure")
        self.diffPressureRadio = QRadioButton("Diff pressure")
        self.O2Radio = QRadioButton("O2")
        self.tidalRadio = QRadioButton("Tidal")

        self.group1 = QButtonGroup()
        self.group2 = QButtonGroup()
        self.radiovbox1 = QHBoxLayout()
        self.radiovbox2 = QHBoxLayout()

        self.radiovbox1.addWidget(self.pressureRadio)
        self.pressureRadio.setChecked(True)
        self.radiovbox1.addWidget(self.diffPressureRadio)

        self.pressureRadio.toggled.connect(lambda:self.btnstate1(0))
        self.diffPressureRadio.toggled.connect(lambda:self.btnstate1(1))

        self.radiovbox2.addWidget(self.O2Radio)
        self.O2Radio.setChecked(True)
        self.radiovbox2.addWidget(self.tidalRadio)

        self.O2Radio.toggled.connect(lambda:self.btnstate2(0))
        self.tidalRadio.toggled.connect(lambda:self.btnstate2(1))
        '''
        """
        self.graphVbox = QVBoxLayout()
        self.graphVbox.addWidget(self.combo1)
        self.graphVbox.addWidget(self.graphStack1)
        #self.graphVbox.addWidget(self.combo2)
        #self.graphVbox.addWidget(self.graphStack2)
        self.graphVbox.addStretch(1)
        """

        self.controlVbox = QVBoxLayout()
        self.controlVbox.addLayout(self.hbox, 1)
        #self.controlVbox.addItem(self.btSpacer)
        #self.controlVbox.addLayout(self.compressionHbox, 2)
        self.controlVbox.addWidget(self.vmWidget, 1)
        self.controlVbox.addWidget(self.rtGridFrame, 8)
        self.controlVbox.addWidget(self.tunerFrame, 8)
        #self.controlVbox.addItem(self.btSpacer)
        self.controlVbox.addWidget(self.updateButton, 1)


        ######## data vertical box layout #######
        self.dataviewVbox = QVBoxLayout()
        #self.dataviewVbox.addWidget(self.statusInd, 1)
        self.dataviewVbox.addLayout(graphview, 8)
        self.dataviewVbox.addLayout(controlgrid, 2)

        self.fullHbox = QHBoxLayout()
        self.fullHbox.addLayout(self.dataviewVbox, 3)
        self.fullHbox.addLayout(self.controlVbox, 1)

        self.setLayout(self.fullHbox)

        #self.setGeometry(0, 0, 790, 470)
        #self.setWindowTitle('Ventilator control unit')
        #self.show()

    def btnstate1(self, idx):
        self.graphStack1.setCurrentIndex(idx)
        if idx == 0:
            self.pressureCanvasVisible = True
            self.diffPressureVisible = False
            self.tidalCanvasVisible = False
            self.o2CanvasVisible = False
        elif idx == 1:
            self.pressureCanvasVisible = False
            self.diffPressureVisible = True
            self.tidalCanvasVisible = False
            self.o2CanvasVisible = False
        elif idx == 2:
            self.pressureCanvasVisible = False
            self.diffPressureVisible = False
            self.tidalCanvasVisible = False
            self.o2CanvasVisible = True
        else:
            self.pressureCanvasVisible = False
            self.diffPressureVisible = False
            self.tidalCanvasVisible = True
            self.o2CanvasVisible = False
        '''
        if idx == 0:
            self.graphStack1.setCurrentIndex(0)
            #self.pressureCanvasVisible = True
            #self.diffPressureVisible = False
        else:
            self.graphStack1.setCurrentIndex(1)
            self.pressureCanvasVisible = False
            self.diffPressureVisible = True
        '''

    def on_currentIndexChanged(self,idx):
        if idx == 1:
            self.ventMode = self.Vent_modes[1];
            self.dsBpm.button.setEnabled(True)
            self.comboIER.setEnabled(True)
            self.dsPh.button.setEnabled(False)
            self.dsVol.button.setEnabled(True)
            self.dsPeep.button.setEnabled(True)
            self.dsFio2.button.setEnabled(True)
        elif idx == 2:
            self.ventMode = self.Vent_modes[2];
            self.dsBpm.button.setEnabled(True)
            self.comboIER.setEnabled(True)
            self.dsPh.button.setEnabled(False)
            self.dsVol.button.setEnabled(True)
            self.dsPeep.button.setEnabled(True)
            self.dsFio2.button.setEnabled(True)
        elif idx == 3:
            self.ventMode = self.Vent_modes[3];
            self.dsBpm.button.setEnabled(True)
            self.comboIER.setEnabled(True)
            self.dsPh.button.setEnabled(True)
            self.dsVol.button.setEnabled(False)
            self.dsPeep.button.setEnabled(True)
            self.dsFio2.button.setEnabled(True)
        elif idx == 4:
            self.ventMode = self.Vent_modes[4];
            self.dsBpm.button.setEnabled(False)
            self.comboIER.setEnabled(False)
            self.dsPh.button.setEnabled(True)
            self.dsVol.button.setEnabled(False)
            self.dsPeep.button.setEnabled(True)
            self.dsFio2.button.setEnabled(True)
        elif idx == 5:
            self.ventMode = self.Vent_modes[5];
            self.dsBpm.button.setEnabled(False)
            self.comboIER.setEnabled(True)
            self.dsPh.button.setEnabled(True)
            self.dsVol.button.setEnabled(True)
            self.dsPeep.button.setEnabled(False)
            self.dsFio2.button.setEnabled(True)
        elif idx == 6:
            self.ventMode = self.Vent_modes[6];
            self.dsBpm.button.setEnabled(False)
            self.comboIER.setEnabled(True)
            self.dsPh.button.setEnabled(True)
            self.dsVol.button.setEnabled(True)
            self.dsPeep.button.setEnabled(False)
            self.dsFio2.button.setEnabled(True)
        else:
            self.dsBpm.button.setEnabled(True)
            self.comboIER.setEnabled(True)
            self.dsPh.button.setEnabled(True)
            self.dsVol.button.setEnabled(True)
            self.dsPeep.button.setEnabled(True)
            self.dsFio2.button.setEnabled(True)

    def onUpdate(self):
        print("pressed update button")
        dataFetched = self.fetchData()
        self.beThread.dataUpdate = dataFetched
        self.bthThread.updateData(dataFetched)

    def btnstate2(self, idx):
        self.graphStack2.setCurrentIndex(idx)
        '''
        if idx==0:
            self.graphStack2.setCurrentIndex(0)
            #self.tidalCanvasVisible = False
            #self.o2CanvasVisible = True
        else:
            self.graphStack2.setCurrentIndex(1)
            self.tidalCanvasVisible = True
            self.o2CanvasVisible = False
        '''

    def disableUI(self):
        '''
        self.spinFio2.setDisabled(True)
        self.spinPeep.setDisabled(True)
        self.comboIER.setDisabled(True)
        self.spinPh.setDisabled(True)
        self.spinBPM.setDisabled(True)
        self.startButton.setDisabled(True)
        '''

        self.startButton.setVisible(False)
        self.stopButton.setVisible(True)
        self.updateButton.setVisible(True)

    def enableUI(self):
        '''
        self.spinFio2.setDisabled(False)
        self.spinPeep.setDisabled(False)
        self.comboIER.setDisabled(False)
        self.spinPh.setDisabled(False)
        self.spinBPM.setDisabled(False)
        self.startButton.setDisabled(False)
        '''
        self.startButton.setVisible(True)
        self.stopButton.setVisible(False)
        self.updateButton.setVisible(False)

    def whichbtn(self,idx):
        if self.dsList[idx].button.isChecked():
            if (self.noCB >= 0):
                self.clearTuner(self.noCB)
            print("button pressed")
            self.rtGridFrame.setVisible(False)
            self.tunerFrame.setVisible(True)
            self.dsList[idx].tuner.setVisible(True)
            self.noCB = idx
        else:
            print("button released")
            self.dsList[idx].tuner.setVisible(False)
            self.tunerFrame.setVisible(False)
            self.rtGridFrame.setVisible(True)
            self.noCB = -1

    def clearTuner(self, idx):
        self.dsList[idx].tuner.setVisible(False)
        self.dsList[idx].button.setChecked(False)

    def sliderMov(self, idx):
        if self.dsList[idx].button.isChecked():
            val = int(self.dsList[idx].tuner.slide.value())
            if ((val) >= self.dsList[idx].tuner.max):
                self.dsList[idx].tuner.value = val = self.dsList[idx].tuner.max
                #self.dsList[idx].tuner.fine = 0
            else:
                self.dsList[idx].tuner.value = val
            self.dsList[idx].button.setText(str(val))
            self.dsList[idx].tuner.label1.setText(str(self.dsList[idx].tuner.value))
            if idx == 0:
                self.priorityIdx = 0
            elif idx == 1:
                self.priorityIdx = 1

    def buttonPlus(self, idx):
        if self.dsList[idx].button.isChecked():
            self.dsList[idx].tuner.value += 1
            if (self.dsList[idx].tuner.value >= self.dsList[idx].tuner.max):
                self.dsList[idx].tuner.value = self.dsList[idx].tuner.max
            self.dsList[idx].button.setText(str(self.dsList[idx].tuner.value) )
            self.dsList[idx].tuner.slide.setValue(self.dsList[idx].tuner.value)
            self.dsList[idx].tuner.label1.setText(str(self.dsList[idx].tuner.value))
            if idx == 0:
                self.priorityIdx = 0
            elif idx == 1:
                self.priorityIdx = 1

    def buttonMinus(self, idx):
        if self.dsList[idx].button.isChecked():
            self.dsList[idx].tuner.value -= 1
            if (self.dsList[idx].tuner.value <= self.dsList[idx].tuner.min):
                self.dsList[idx].tuner.value = self.dsList[idx].tuner.min
            self.dsList[idx].button.setText(str(self.dsList[idx].tuner.value) )
            self.dsList[idx].tuner.slide.setValue(self.dsList[idx].tuner.value)
            self.dsList[idx].tuner.label1.setText(str(self.dsList[idx].tuner.value))
            if idx == 0:
                self.priorityIdx = 0
            elif idx == 1:
                self.priorityIdx = 1
