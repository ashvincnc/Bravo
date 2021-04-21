import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
#from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, QGridLayout, 
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSlot,pyqtSignal
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import sys  
import os
from random import randint
import json
import serial
import time
from PyQt5.QtCore import QThread
global pressure_pdata
global fio2_pdata
global lpressure
import threading
import RPi.GPIO as GPIO
global ini
ini = 0
global rap,data_line
rap = 0
GPIO.setmode(GPIO.BCM)
import Adafruit_ADS1x15

import sys

global gf

sys.setrecursionlimit(10**3)
global adc
adc = Adafruit_ADS1x15.ADS1115(address=0x48)

global pressure_val,volume_val,fio_val,peep_val
global in_time,out_time
global graph
global mod_val
global data_m
global trigger_data
trigger_data = 0


GAIN = 1


class breathWorker(QThread):
    
#    sigDataupdate = Signal(dict)
    stopSignal = pyqtSignal()
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

        GPIO.setup(12, GPIO.OUT)
        GPIO.setup(13, GPIO.OUT)
        
        GPIO.setup(14, GPIO.OUT)
        
        GPIO.setup(26, GPIO.OUT)
        GPIO.output(14,GPIO.HIGH)
        self.o2PWM = GPIO.PWM(12, 50)
        self.pPWM = GPIO.PWM(13, 50)
###
        
    def update_pwm_Data(self):
        global pressure_val,volume_val,fio_val
        global in_time,out_time
        
      #  self.fetch_data()
        ###
        '''
        pressure_pdata= int(lpressure.text())
        global fio2_data
        fio2_data= int(lfio2.text())
        global volume_pdata
        volume_pdata = int(lvol.text())
        print('p_data',pressure_pdata)
        print('f_data',fio2_data)
        print('v_data',volume_pdata)
        '''
        ###
        pressure_pdata = int(pressure_val)
        print('p_data',pressure_pdata)
        volume_pdata = int(volume_val)
        print('v_data',volume_pdata)
        fio2_data = int(fio_val)   
        print('f_data',fio2_data)
        
        
        #self._key_lock.acquire()
        #self.o2DC = pressure_pdata
        #self.pDC = fio2_data
        pressPercent = 0
        oxyPercent = 0
        if(fio2_data)>21 and fio2_data > 50:
            oxy_value = float(fio2_data)/100
            pressPercent = float(volume_pdata) * (1-oxy_value)
            oxyPercent = float(volume_pdata) * oxy_value
        elif(fio2_data)>21 and fio2_data < 51:
            oxy_value = float(fio2_data)/100
            pressPercent = float(volume_pdata) * oxy_value
            oxyPercent = float(volume_pdata) * (1-oxy_value)
        else:
            pressPercent = volume_pdata
            oxyPercent = 0
            
        print("Percents: ", pressPercent,oxyPercent)
        self.pressureCycleValue = self.readPressureValues(pressPercent,oxyPercent)
        print("pressureCycleValue")
        print(self.pressureCycleValue)
        self.intime = in_time
        self.outtime = out_time
        self.in_t = self.intime / 1000
        self.out_t =  self.outtime /1000
        print('in-time',in_time)
        print('out-time',out_time)
        print("In and out" + str(self.in_t) + str(self.out_t))
   #     self.peep = self.lpeep.text()
  
        

    def stop(self):
        print("stopping breather thread")
        GPIO.output(14,GPIO.HIGH)
        GPIO.output(26,GPIO.HIGH)
        self.running = False

    def run(self):
        global graph,mod_val_data
        global mod_val
        mod_val = 1
        GPIO.output(14,GPIO.LOW)
        self.o2PWM.start(0)
        self.pPWM.start(0)
#        print("starting breather thread"+ str(self.o2DC)+str(self.pDC)+str(self.in_t)+str(self.out_t)+str(self.peep))
        QThread.msleep(1)
        i = True
      
        end = time.time()+15
    
        ###
        '''
        if (mod_val == 4):
             print('in mode4')
             while self.running:
                 if(i==True):
                    while(time.time()<end):
                        if (mod_val_data == 1):
                            print('in')
                            self.pwm_in()
                          #  mod_val_data = 0
                            a = 1
                            i = False
                            break
                        
                        else:
                            print('ex')
                            self.pwm_out()

                 if (a == 1):
                        print('in mode 4 conti')
                        if (mod_val_data == 1):
                            print('in')
                            self.pwm_in()
                            mod_val_data = 0
                        else:
                            print('ex')
                            self.pwm_out()
                 if(mod_val_data == 0):
                     print('mode changed to 0')
                     mod_val = 0
                     break
   '''
        ###
           
        if (mod_val == 1):
            print('mode 1 enabled')
            while self.running:
                self.pwm_in()
                self.pwm_out()
        if (mod_val == 5):
            print('mode 5 enabled')
            while self.running:
                print('mode 5')
                self.pwm_in()
                if(self.running != True):
                    print('mode 5 off')
                    self.pwm_out()
                    break
        print('mode : ',mode_val)       
               
   

    def pwm_in(self):
                global graph,rap
                print("self.running.loop")
                graph = 0
                self.pPWM.ChangeDutyCycle(self.pressureCycleValue[0])
                self.o2PWM.ChangeDutyCycle(self.pressureCycleValue[1])
                rap = 0
                GPIO.output(26,GPIO.HIGH)
                GPIO.output(14,GPIO.LOW)
                self.breathStatus = 0
                             
                self._inhale_event.wait(timeout=self.in_t)
    def pwm_out(self):
                global graph,peep_val,rap
                self.peep = peep_val
                print('peep',peep_val)
           #     print(self.peep)
                print("pwm_out")
                graph = 1
                self.o2PWM.ChangeDutyCycle(self.peep)
                self.pPWM.ChangeDutyCycle(self.peep)
                GPIO.output(26,GPIO.LOW)
                self.breathStatus = 1
                self._exhale_event.wait(timeout=self.out_t)
                rap = 1
                print('rap')
                
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
    threadSignal = pyqtSignal(dict)
    stopSignal =  pyqtSignal()
    dataUpdate = None
    firstLaunch = True
    currentVolData = 0
    global gf


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
        
        print('init_ser')
        
        ###
        '''
            
            self.ser = serial.Serial("/dev/ttyUSB1",9600)  #change ACM number as found from ls /dev/tty/ACM*
            #self.ser1 = serial.Serial("/dev/ttyUSB1",9600)
            self.ser.baudrate=9600
            #self.ser1.baudrate=9600
        '''
        ###
        
    def sendValues(self):
        #GPIO.output(4,GPIO.HIGH)
        #time.sleep(0.2)
        #GPIO.output(pin,GPIO.LOW)
        data2transfer = self.dataUpdate["pressure"]+','+self.dataUpdate["intime"]+','+self.dataUpdate["outtime"]+','+self.dataUpdate["peep"]+','+self.dataUpdate["fio2"]
        print("DEBUG: "+data2transfer)
        #self.ser1.write(data2transfer.encode())

    def getdata(self):
        global gf
        global ini,rap,adc
        
        global firstvalue
        global graph,mod_val,data
        
      #  print('getdata_init')
        read_ser = []
        
        print('getdata')
        data = [0]*4  
        endtime = time.time()+0.1
        while(time.time()<endtime):
            
            for i in range(4):
                try:  
                    data[i] = adc.read_adc(i, gain=GAIN)
                    print('i ,data',i,data[i])
                except:
                    print('i2c error')
                
         #   data_s = data.rstrip()
         #   data_string = str(data_s)
        #    data = list(data_string.split(","))
            #sleep(0.3)
            pressurel = []
            pressurel.append(int(data[3]))
            print('presss',pressurel)
            time.sleep(0.5)
  
        pressurel.sort(reverse = True)
        
    #    print('test',pressurel[0])
        
        if(graph == 0):
            
            print('Inhaling')

            if(ini == 0):
                    firstvalue = pressurel[0]
                    print('firstvalue',firstvalue)
                    currentPressure = firstvalue
                    ini += 1
                    print('ini',ini)
            else:
                    nextvalue = pressurel[0]
                    if(nextvalue > firstvalue):
                        currentPressure = nextvalue
                        firstvalue = currentPressure
                    if(nextvalue < firstvalue):
                        currentPressure = firstvalue
                        firstvalue = currentPressure
                    print('cpp',currentPressure)        
            if (currentPressure < pressurel[0]):
                currentPressure = pressurel[0]
            else:
               currentPressure = firstvalue
            print('cp',currentPressure)
            if(len(self.dataDict["Dpress+"])>300):
                self.dataDict.clear()
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
            self.dataDict["Dpress+"].append(currentPressure)   
        if (graph == 1):
            print('Exhaling')
            currentPressure = int(data[3])
            print('exale pree',currentPressure)
            if(mod_val == 4):
                    print('mode_4')
                    if (currentPressure < _trigger):
                        mod_val_data = 1
                        print('pressure_low')
                    else:
                        mod_val_data = 0
                        print('pressure_normal')
                  #     if (mod_val == 4):
       #         currentPressure = int(data[3])
       #         if (currentPressure < 400):
       #             print('below',currentPressure)
       #             mod_val_data = 1
               #           print('cp',currentPressure)
 #           print('sensor-mod',mod_val_data)
            
            if(len(self.dataDict["Dpress+"])>300):
                self.dataDict["Dpress+"].clear()
                gf = 1
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
                
            self.dataDict["Dpress+"].append(currentPressure)
                
        print('g',self.dataDict)
        return self.dataDict
        
#         print('sos',sos)
        #if len(data) < 10:
         #   print("dropping data")
            #return None
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
 #       self.data_line.setData(self.x, self.y) 
        self.dataDict["o2conc"].append(int(data[1]))
        self.dataDict["AirV"].append(int(data[2]))
       # print('o2conc_airv')
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

        if len(self.dataDict["o2conc"]) >180:
            self.dataDict["o2conc"].pop(0)
            self.dataDict["AirV"].pop(0)
            self.dataDict["Dpress+"].pop(0)
            self.dataDict["Dpress-"].pop(0)
            self.dataDict["press+"].pop(0)
            self.dataDict["press-"].pop(0)
            self.dataDict["co2"].pop(0)
            self.dataDict["temp"].pop(0)
            #self.dataDict["hum"].pop(0)
      
        print('g',self.dataDict)    
        
        return self.dataDict

    def run(self):
        global data_m
        # Do something...
        if self.firstLaunch :
            self.initSerData()
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
        print('bworker',data_m)
        #self.threadSignal.emit(self.startParm)



class App(QDialog):

    def __init__(self):
        super().__init__()
        self.title = 'ventilator'
        
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 100
        
        self.initUI()

       # self.graph3()
        self.setStyleSheet("background-color: black;")
        
        self.bthThread = breathWorker()
        self.bthThread.stopSignal.connect(self.bthThread.stop)
        
        self.beThread = backendWorker('hello')
  #      self.beThread.threadSignal.connect(self.updateData)
        self.beThread.stopSignal.connect(self.beThread.stop)
        self.update_parameters()
        self.graph()
        #self.graph2()
        
        
        

        
    def fetch_data(self):
        
        ## computing breathing intervals ##
        global in_time,out_time
        ie_pdata =2
        bpm = self.lbpm.text()
        if self.lie.text() == '0:0':      
            ie_pdata = 2
        if self.lie.text() == '1.1':      
            ie_pdata = 3
        if self.lie.text() == '1.2':      
            ie_pdata = 4
        if self.lie.text() == '1.3':      
            ie_pdata = 5
        if self.lie.text() == '1.4':      
            ie_pdata = 6
        print('ie',ie_pdata)   
# # # # # # # # # #         print('ie'+str(ie_pdata))
        self.breathCount = 60 / int(bpm)
        print('breathcount',self.breathCount)
    
        self.inhaleTime = (self.breathCount/2) * 1000 - 0.5
        self.exhaleTime = (self.breathCount * 1000) - self.inhaleTime
                
        in_time = self.inhaleTime
        out_time = self.exhaleTime
        print(self.exhaleTime)
        
            #self._key_lock.release()    

    def update_parameters(self):
        self.pressure_value = False 
        self.volume_value = False
        self.bpm_value = False
        self.fio2_value = False
        self.peep_value = False   
        
    def graph(self):
        global rap
        global gf
        self.graphwidget = pg.PlotWidget()
        #self.x = list(range(100))  # 100 time points
        self.y = [randint(0,0) for _ in range(300)]  # 100 data points
        
        
        self.graphwidget.setBackground('#0000')
        self.graphwidget.getPlotItem().hideAxis('bottom')

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line =  self.graphwidget.plot(self.y, pen=pen) #fillLevel=0,brush=(150,50,150,50))           #pen=pen)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()
        self.layout.addWidget(self.graphwidget,2,0,5,4)
        #self.data_line.clear()

    def update_plot_data(self):
        
        global data_m,rap
        a = 0
        
        if self.bthThread.breathStatus == 0:
            self.lbcadata.setText('Inhale')
            press = self.lpresd.text()
            self.lpresd.setText(press)
            self.lbtidata.setText('8')
            #self.lpbdata.setText(press)
            vol = self.lvol.text()
            volc = int(vol) +int(randint(-10,5))
            self.lbvedata.setText(str(volc))
            peep = int(self.lpeep.text()) + randint(0,10)
            self.lbpeepdata.setText('-')
            
            
            
        if self.bthThread.breathStatus == 1:
            self.lbcadata.setText('Exhale')
            self.lpresd.setText('0')
            self.lbtidata.setText('-')
            #self.lpbdata.setText(press)
            vol = self.lvol.text()
            volc = int(vol)+int(randint(-10,5))
            self.lbvedata.setText(str(vol))
            peep = int(self.lpeep.text()) + randint(0,10)
            self.lbpeepdata.setText(str(peep))
        
        try:
                self.y = self.y[1:]
                self.y.append(int(data_m['Dpress+'][-1]))
                #print('try',data_m['Dpress+'][-1])
                #print('y',self.y)
                self.data_line.setData(self.y)

        except:
            print('NO sensor data recevied')
 
        #print('graph_plot')
         
        #if(rap == 1):
           # self.data_line.clear()
           # print('graph_clear')
       # Update the data.
        
            
        
    def graph2(self):
        self.graphWidget = pg.PlotWidget()
        self.x2 = list(range(100))  # 100 time points
        self.y2 = [randint(0,100) for _ in range(100)]  # 100 data points

        self.graphWidget.setBackground('#0000')

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line2 =  self.graphWidget.plot(self.x2, self.y2, pen=pen)
        self.timer1 = QtCore.QTimer()
        self.timer1.setInterval(100)
        self.timer1.timeout.connect(self.update_plot_data2)
        self.timer1.start()
        self.layout.addWidget(self.graphWidget,3,0,3,4)

    def update_plot_data2(self):

        self.x2 = self.x2[1:]  # Remove the first y element.
        self.x2.append(self.x2[-1] + 1)  # Add a new value 1 higher than the last.

        self.y2 = self.y2[1:]  # Remove the first 
        self.y2.append( randint(0,100))  # Add a new random value.

        self.data_line2.setData(self.x2, self.y2)  # Update the data.

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
        self.readSettings(0)
        self.createGridLayout()
        
        
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)

        self.setLayout(windowLayout)
        
        self.showFullScreen()
    def readSettings(self,i):
        global mod_val
        params = ["pressure", "volume", "bpm", "peep", "fio2"]
        # reading the data from the file
        
        if(i == 0):
        
            with open('settings.txt') as f:
                data = f.read()
                print('default')
        
        if(i == 1):
               with open('mode1.txt') as f:
                data = f.read()
              #  print('default')
        if(i == 2):
               with open('mode2.txt') as f:
                data = f.read()      
        if(i == 3):
               with open('mode3.txt') as f:
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
             
    
    def label_reset(self):
        self.lpressure.setText('0')
        self.lvol.setText('0')
        self.lbpm.setText('0')
        self.lpeep.setText('0')
        self.lfio2.setText('0')
        
    def stop_action(self):
        Bstart = QPushButton('Start')          #start button
        Bstart.setFont(QFont('Arial', 15))
        Bstart.setStyleSheet("background-color: white")
        Bstart.clicked.connect(self.on_process)
        self.layout.addWidget(Bstart,9,6)
        Bstart.clicked.connect(self.stop)

        
        
    def stop(self):
        self.bstop = QPushButton('stop')
        self.bstop.setFont(QFont('Arial', 15))
        self.bstop.setStyleSheet("background-color: grey")
        self.layout.addWidget(self.bstop,9,6)
        self.bstop.clicked.connect(self.off_process)
        self.bstop.clicked.connect(self.stop_action)
        
        
    def ps(self):
        
        self.label_reset()
        self.readSettings(1)
        
        self.lpressure.setText(str(self.settings["pressure"]["default"]))
        self.lvol.setText(str(self.settings["volume"]["default"]))
        self.lbpm.setText(str(self.settings["bpm"]["default"]))
        self.lpeep.setText(str(self.settings["peep"]["default"]))
        self.lfio2.setText(str(self.settings["fio2"]["default"]))
        
    def hfonc(self):
        self.label_reset()
        self.readSettings(2)
        
        self.lpressure.setText(str(self.settings["pressure"]["default"]))
        self.lvol.setText(str(self.settings["volume"]["default"]))
        self.lbpm.setText(str(self.settings["bpm"]["default"]))
        self.lpeep.setText(str(self.settings["peep"]["default"]))
        self.lfio2.setText(str(self.settings["fio2"]["default"]))
        
    def pc(self):
        self.label_reset()
        self.readSettings(3)
        
        self.lpressure.setText(str(self.settings["pressure"]["default"]))
        self.lvol.setText(str(self.settings["volume"]["default"]))
        self.lbpm.setText(str(self.settings["bpm"]["default"]))
        self.lpeep.setText(str(self.settings["peep"]["default"]))
        self.lfio2.setText(str(self.settings["fio2"]["default"]))
        
    def value_set(self):
       
        self.sl = QSlider(Qt.Vertical, self) 
        self.sl.setRange(0, 100)  
        self.sl.setFocusPolicy(Qt.NoFocus)
        self.sl.setPageStep(5)
        self.sl.valueChanged.connect(self.updateLabel)
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
        self.update_val.setFont(QFont('Arial', 20))  
        self.update_val.setStyleSheet("background-color: red")
        self.layout.addWidget(self.update_val,7,6)
        self.update_val.clicked.connect(self.update_set)    
    
    def volume_set(self):
       
        self.slv = QSlider(Qt.Vertical, self)
        self.slv.setRange(50, 2000)  
        self.slv.setFocusPolicy(Qt.NoFocus)
        self.slv.setPageStep(5)
        self.slv.setGeometry(QtCore.QRect(390,300,360,36))
        self.slv.valueChanged.connect(self.updateLabel)
        self.slv.setTickPosition(QSlider.TicksBelow)
        self.slv.setTickInterval(5)

        self.label = QLabel('0', self)
        self.label.setAlignment(Qt.AlignRight | Qt.AlignRight)
        self.label.setMinimumWidth(80)
        self.label.setFont(QFont('Arial', 25))
        self.label.setStyleSheet("color: white;  background-color: black")

        self.layout.addWidget( self.slv,2,6,4,2,alignment=Qt.AlignLeft)
        self.layout.addWidget(self.label,6,6)

        self.update_val = QPushButton('Update')
        self.update_val.setFont(QFont('Arial', 20))  
        self.update_val.setStyleSheet("background-color: red")
        self.layout.addWidget(self.update_val,7,6)
        self.update_val.clicked.connect(self.lvolume_set)
        
    def update_set(self):
        global pressure_val,volume_val,fio_val,peep_val
        #print(self.updated_value) #Updated value
        if (self.pressure_value == True):
            self.lpressure.setText(self.updated_value)
            pressure_val = int(self.lpressure.text())
            self.pressure_value = False
        if (self.volume_value == True):
            self.lvol.setText(self.updated_value)
            volume_val = int(self.lvol.text())
            self.volume_value = False
        if(self.bpm_value == True):
            self.lbpm.setText(self.updated_value)
            self.bpm_value = False
        if(self.fio2_value == True):
            self.lfio2.setText(self.updated_value)
            fio_val = self.lfio2.text()
            self.fio2_value = False
        if(self.peep_value == True):
            self.lpeep.setText(self.updated_value)
            peep_val = int(self.lpeep.text())
            self.peep_value == False
  
        self.sl.deleteLater()
        self.label.deleteLater()
        self.update_val.deleteLater()
        self.update_parameters()    
        
    def lvolume_set(self):
        global pressure_val,volume_val,fio_val,peep_val
        #print(self.updated_value) #Updated value
        if (self.pressure_value == True):
            self.lpressure.setText(self.updated_value)
            pressure_val = int(self.lpressure.text())
            self.pressure_value = False
        if (self.volume_value == True):
            self.lvol.setText(self.updated_value)
            volume_val = int(self.lvol.text())
            self.volume_value = False
        if(self.bpm_value == True):
            self.lbpm.setText(self.updated_value)
            self.bpm_value = False
        if(self.fio2_value == True):
            self.lfio2.setText(self.updated_value)
            fio_val = self.lfio2.text()
            self.fio2_value = False
        if(self.peep_value == True):
            self.lpeep.setText(self.updated_value)
            peep_val = int(self.lpeep.text())
            self.peep_value == False
  
        self.slv.deleteLater()
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
      self.cb.setFont(QFont('Arial', 13))
      self.cb.setStyleSheet("color: black;  background-color: white") 
      self.cb.setGeometry(200, 150, 120, 40)  
      self.layout.addWidget(self.cb,6,4)
      self.cb.currentIndexChanged.connect(self.ie_updated)

    def ie_updated(self, value):
        self.cb.deleteLater()
        self.ie_value = str(value)
        
        if(self.ie_value == '1'):
            self.lie.setText('1:1')
        if(self.ie_value == '2'):
            self.lie.setText('1:2')
        if(self.ie_value == '3'):
            self.lie.setText('1:3')
        if(self.ie_value == '4'):
            self.lie.setText('1:4')        

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
      self.cbtr.setFont(QFont('Arial', 13))
      self.cbtr.setStyleSheet("color: black;  background-color: white") 
      self.cbtr.setGeometry(200, 150, 120, 40)  
      self.layout.addWidget(self.cbtr,4,4)
      self.cbtr.currentIndexChanged.connect(self.trigger_updated)

    def trigger_updated(self, value):
        self.cbtr.deleteLater()
        self.trigger_value = str(value)
        if self.trigger_value == '1':
            self.ltrigger.setText("-10")
        if self.trigger_value == '2':
            self.ltrigger.setText("-9")
        if self.trigger_value == '3':
            self.ltrigger.setText("-8")
        if self.trigger_value == '4':
            self.ltrigger.setText("-7")
        if self.trigger_value == '5':
            self.ltrigger.setText("-6")
        if self.trigger_value == '6':
            self.ltrigger.setText("-5")
        if self.trigger_value == '7':
            self.ltrigger.setText("-4")
        if self.trigger_value == '8':
            self.ltrigger.setText("-3")
                                        
        global trigger_data
        trigger_data = int(self.ltrigger.text())
        print('t_data',trigger_data)                                
        #print(self.trigger_value)

    def mode_update(self):

      self.md = QComboBox()
      self.md.addItem("Modes")
      self.md.addItem("None")
      #self.md.addItem("PRVC")
      self.md.addItem("VC")
      self.md.addItem("PC")
      self.md.addItem("SPONT+PS")
      self.md.addItem("HFONC")
      self.md.addItem("BiPAP")
      self.md.setFont(QFont('Arial', 10))
      self.md.setStyleSheet("color: black;  background-color: white") 
      self.md.setGeometry(200, 150, 120, 40)  
      self.layout.addWidget(self.md,2,4)
      self.md.currentIndexChanged.connect(self.mode_updated)

    def mode_updated(self, value):
        global mod_val
        self.md.deleteLater()
        self.mode_set = str(value)
        if self.mode_set == '1':
            self.lmode.setText('None')
            mod_val = 1
            print('mode_val',mod_val)
        if self.mode_set == '2':
            self.lmode.setText('VC')
        if self.mode_set == '3':
            self.lmode.setText('PC')
            self.pc()
        if self.mode_set == '4':
            self.ps()
            self.lmode.setText('SPONT+PS')
            mod_val = 4
            print('mode_val',mod_val)
        if self.mode_set == '5':
            self.hfonc()
            self.lmode.setText('HFONC')
            mod_val = 5
            print('mode_val',mod_val)
        if self.mode_set == '6':
            self.lmode.setText('BiPAP')
            mod_val = 4
            print('mode_val',mod_val)
    def on_process(self):
        print("pressed start button")
    #    dataFetched = self.fetchData()
    #    self.beThread.dataUpdate = dataFetched
        self.fetch_data()
        self.bthThread.update_pwm_Data()
        self.beThread.running = True
        self.bthThread.running = True
  #      self.disableUI()
        self.beThread.start()
        self.bthThread.start()
        
    def off_process(self):
        print("pressed stop button")
        self.beThread.stopSignal.emit()
        self.bthThread.stopSignal.emit()
        print('closed')
        
    def createGridLayout(self):
        global lpressure
        global pressure_val,volume_val,fio_val,peep_val
        self.horizontalGroupBox = QGroupBox() 
        self.layout = QGridLayout()
        self.layout.setColumnStretch(6, 9)
        self.layout.setColumnStretch(6, 9)     

        #Adding push buttons
        Bpressure = QPushButton('Pressure') #pressurepush button
        Bpressure.setGeometry(0, 0, 100, 40)
        Bpressure.setFont(QFont('Arial', 15))  
        Bpressure.setStyleSheet("background-color: white")
        self.layout.addWidget(Bpressure,7,0)
        
        Bpressure.clicked.connect(self.value_set)
        Bpressure.clicked.connect(self.pressure_update)

        self.lpressure = QLabel("0")  #pressure label
        self.lpressure.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lpressure.setFont(QFont('Arial', 15))
        self.lpressure.setStyleSheet("color: white;  background-color: black")
 #       
        a = str(self.settings["pressure"]["default"])
        self.lpressure.setText(a)
        pressure_val = int(self.lpressure.text())
        self.layout.addWidget(self.lpressure,8,0)
        
        Bvol = QPushButton('Volume') #volumePushButton
        Bvol.setGeometry(0, 0, 100, 40)
        Bvol.setFont(QFont('Arial', 15))
        Bvol.setStyleSheet("background-color: white")
        self.layout.addWidget(Bvol,7,1)
        Bvol.clicked.connect(self.volume_update)
        Bvol.clicked.connect(self.volume_set)
        
        
        self.lvol = QLabel("0")  #volume label
        self.lvol.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lvol.setFont(QFont('Arial', 15))
        self.lvol.setStyleSheet("color: white;  background-color: black")
        a = str(self.settings["volume"]["default"])
        self.lvol.setText(a)
        volume_val = int(self.lvol.text())
        self.layout.addWidget(self.lvol,8,1)
  
        Bbpm = QPushButton('BPM')  #BPM PushButton
        Bbpm.setGeometry(0, 0, 100, 40)
        Bbpm.setFont(QFont('Arial', 15))
        Bbpm.setStyleSheet("background-color: white")
        self.layout.addWidget(Bbpm,7,2)
        Bbpm.clicked.connect(self.value_set)
        Bbpm.clicked.connect(self.bpm_update)

        self.lbpm = QLabel("0")  #BPM label
        self.lbpm.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lbpm.setFont(QFont('Arial', 15))
        self.lbpm.setStyleSheet("color: white;  background-color: black")
        a = str(self.settings["bpm"]["default"])
        self.lbpm.setText(a)
        self.layout.addWidget(self.lbpm,8,2)

        Bpeep = QPushButton('PEEP')  #peep_button
        Bpeep.setGeometry(0, 0, 100, 40)
        Bpeep.setFont(QFont('Arial', 15))  
        Bpeep.setStyleSheet("background-color: white")
        self.layout.addWidget(Bpeep,7,3)
        Bpeep.clicked.connect(self.value_set)
        Bpeep.clicked.connect(self.peep_update)

        self.lpeep = QLabel("0")  #peep label
        self.lpeep.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lpeep.setFont(QFont('Arial', 15))
        self.lpeep.setStyleSheet("color: white;  background-color: black")
        a = str(self.settings["peep"]["default"])
        self.lpeep.setText(a)
        peep_val = int(self.lpeep.text())
        self.layout.addWidget(self.lpeep,8,3)

        Bfio2 = QPushButton('fio2')  #fio2 Button
        Bfio2.setGeometry(0, 0, 100, 40)
        Bfio2.setFont(QFont('Arial', 15))
        Bfio2.setStyleSheet("background-color: white")
        self.layout.addWidget(Bfio2,8,4)
        Bfio2.clicked.connect(self.value_set)
        Bfio2.clicked.connect(self.fio2_update)

        self.lfio2 = QLabel("0")  #fio2 label
        self.lfio2.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lfio2.setFont(QFont('Arial', 15))
        self.lfio2.setStyleSheet("color: white;  background-color: black")
        a = str(self.settings["fio2"]["default"])
        self.lfio2.setText(a)
        fio_val = int(self.lfio2.text())
        self.layout.addWidget(self.lfio2,9,4)

        Bmode = QPushButton('Mode') #mode button
        Bmode.setGeometry(0, 0, 100, 400)
        Bmode.setFont(QFont('Arial', 15))
        Bmode.setStyleSheet("background-color: white")
        self.layout.addWidget(Bmode,3,4)
        Bmode.clicked.connect(self.mode_update)

        Btrigger = QPushButton('Trigger')  #trigger button
        Btrigger.setGeometry(0, 0, 100, 40)
        Btrigger.setFont(QFont('Arial', 15))
        Btrigger.setStyleSheet("background-color: white")
        self.layout.addWidget(Btrigger,4,4)
        Btrigger.clicked.connect(self.trigger_update)

        self.ltrigger = QLabel("0")  #trigger label
        self.ltrigger.setFont(QFont('Arial', 15))
        self.ltrigger.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(self.ltrigger,5,4)

        self.BIE = QPushButton('I:E')    #IE button
        self.BIE.setGeometry(0, 0, 100, 40)
        self.BIE.setFont(QFont('Arial', 15))
        self.BIE.setStyleSheet("background-color: white")
        self.layout.addWidget(self.BIE,6,4)
        self.BIE.clicked.connect(self.ie_update)

        self.lie = QLabel("0:0")  #IE label
        self.lie.setFont(QFont('Arial', 15))
        self.lie.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(self.lie,7,4)

        self.lmode = QLabel("Modes")  #mode label
        self.lmode.setFont(QFont('Arial', 13))
        self.lmode.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(self.lmode,2,4)

        ratio = '1:1'                  #breath ratio label
        lbr = QLabel('Breath Ratio')
        lbr.setFont(QFont('Arial', 10))
        lbrdata = QLabel(ratio)
        lbrdata.setFont(QFont('Arial', 25))
        lbr.setStyleSheet("color: white;  background-color: black")
        lbrdata.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(lbr,1,5)
        self.layout.addWidget(lbrdata,2,5)

        pip = '0'                      #pip label       
        lbP = QLabel('PIP')
        lbP.setFont(QFont('Arial', 10))
        self.lbpdata = QLabel(pip)
        self.lbpdata.setFont(QFont('Arial', 25))
        lbP.setStyleSheet("color: white;  background-color: black")
        self.lbpdata.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(lbP,3,5)
        self.layout.addWidget(self.lbpdata,4,5)

        pmean = '0'                      #mean label    
        lbpmean = QLabel('P Mean')
        lbpmean.setFont(QFont('Arial', 10))
        self.lbpmeandata = QLabel(pmean)
        self.lbpmeandata.setFont(QFont('Arial', 25))
        lbpmean.setStyleSheet("color: white;  background-color: black")
        self.lbpmeandata.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(lbpmean,5,5)
        self.layout.addWidget(self.lbpmeandata,6,5)

        ti = '0'                          #Ti label
        lbti = QLabel('Ti')
        lbti.setFont(QFont('Arial', 10))
        self.lbtidata = QLabel(ti)
        self.lbtidata.setFont(QFont('Arial', 25))
        lbti.setStyleSheet("color: white;  background-color: black")
        self.lbtidata.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(lbti,7,5)
        self.layout.addWidget(self.lbtidata,8,5)

        ca = 'Exhale'                      #current activity label
        lbca = QLabel('Current Activity')
        lbca.setFont(QFont('Arial', 10))
        self.lbcadata = QLabel(ca)
        self.lbcadata.setFont(QFont('Arial', 15))
        lbca.setStyleSheet("color: white;  background-color: black")
        self.lbcadata.setStyleSheet("color: white;  background-color: black")
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
        Bstart.setFont(QFont('Arial', 15))
        Bstart.setStyleSheet("background-color: white")
        Bstart.clicked.connect(self.on_process)
        self.layout.addWidget(Bstart,9,6)
        Bstart.clicked.connect(self.stop)
        
        self.lalarm = QLabel('Alarm')
        self.lalarm.setFont(QFont('Arial', 15))
        self.lalarm.setStyleSheet("color: white;  background-color: black")
        self.lalarm.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lalarm,0,0)
         
         
        self.lgas = QLabel('Gas-Flur')
        self.lgas.setFont(QFont('Arial', 15))
        self.lgas.setStyleSheet("color: white;  background-color: black")
        self.lgas.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lgas,0,1)
        
        self.lgas = QLabel('Gas-Flur')
        self.lgas.setFont(QFont('Arial', 15))
        self.lgas.setStyleSheet("color: white;  background-color: black")
        self.lgas.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lgas,0,1)

        self.lgasd = QLabel('0')
        self.lgasd.setFont(QFont('Arial', 15))
        self.lgasd.setStyleSheet("color: white;  background-color: black")
        self.lgasd.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lgasd,1,1)

        self.lapr = QLabel('APR')
        self.lapr.setFont(QFont('Arial', 15))
        self.lapr.setStyleSheet("color: white;  background-color: black")
        self.lapr.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lapr,0,2)

        self.laprd = QLabel('0')
        self.laprd.setFont(QFont('Arial', 15))
        self.laprd.setStyleSheet("color: white;  background-color: black")
        self.laprd.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.laprd,1,2)

        self.lpres = QLabel('Pressure')
        self.lpres.setFont(QFont('Arial', 15))
        self.lpres.setStyleSheet("color: white;  background-color: black")
        self.lpres.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lpres,0,3)

        self.lpresd = QLabel('0')
        self.lpresd.setFont(QFont('Arial', 15))
        self.lpresd.setStyleSheet("color: white;  background-color: black")
        self.lpresd.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lpresd,1,3)

        self.lmv = QLabel('MV')
        self.lmv.setFont(QFont('Arial', 15))
        self.lmv.setStyleSheet("color: white;  background-color: black")
        self.lmv.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lmv,0,4)

        self.lmvd = QLabel('0')
        self.lmvd.setFont(QFont('Arial', 15))
        self.lmvd.setStyleSheet("color: white;  background-color: black")
        self.lmvd.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lmvd,1,4)


        self.lrr = QLabel('RR')
        self.lrr.setFont(QFont('Arial', 15))
        self.lrr.setStyleSheet("color: white;  background-color: black")
        self.lrr.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lrr,0,5) 

        self.lrrd = QLabel('0')
        self.lrrd.setFont(QFont('Arial', 15))
        self.lrrd.setStyleSheet("color: white;  background-color: black")
        self.lrrd.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lrrd,1,5) 

        self.llogo = QLabel('Bravo...')
        self.llogo.setFont(QFont('Gabriola', 25))
        self.llogo.setStyleSheet("color: maroon;  background-color: black")
        self.llogo.setAlignment(Qt.AlignLeft | Qt.AlignLeft)
        self.layout.addWidget(self.llogo,9,0) 
  
        
        self.lpower = QLabel('POWER')
        self.lpower.setFont(QFont('Arail', 13))
        self.lpower.setStyleSheet("color: white;  background-color: green")
        self.lpower.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lpower,0,6) 

        self.horizontalGroupBox.setLayout(self.layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
