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
global ini,kz
ini = 0
kz = 0
global rap,data_line
rap = 0
GPIO.setmode(GPIO.BCM)
import Adafruit_ADS1x15

import sys

global gf,ti
ti = 0
global plan
global rr_value,i_rr
i_rr = 0
rr_value= 0
plan = 0
sys.setrecursionlimit(10**3)
global adc
adc = Adafruit_ADS1x15.ADS1115(address=0x48)
global pressure_support
global pressure_val,volume_val,fio_val,peep_val
global in_time,out_time
global graph,ps_change
global mod_val,mod_val_data,value
value = 0
mod_val_data = 0
mod_val = 1
ps_change = 0
global data_m,control,ti_value
global trigger_data,ps_control
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
    #    print("setup pwm ")
        

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
        global pressure_val,volume_val,fio_val,mod_val
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
        
  #      print('pressure_pdata',pressure_pdata)

        
        
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
        if(mod_val == 1 or mod_val == 5):
            self.pressureCycleValue = self.readPressureValues(pressPercent,oxyPercent)
        if(mod_val == 4):
            self.pressureCycleValue = self.readPressureValues(502,1)
        if(mod_val == 2)  :
            pressure_pdata = pressure_pdata*30
            self.pressureCycleValue = self.readPressureValues(pressure_pdata,oxyPercent)
            print('pre30',pressure_pdata)
            
        print("pressureCycleValue")
        print(self.pressureCycleValue)
        self.intime = in_time
        self.outtime = out_time
        self.in_t = self.intime - 0.3 
        self.out_t =  self.outtime + 0.3 
        print('in-time',in_time)
        print('out-time',out_time)
        print("In and out" + str(self.in_t) + str(self.out_t))
   #     self.peep = self.lpeep.text()
  
        

    def stop(self):
        print("stopping breather thread")
        self.pPWM.ChangeDutyCycle(0)
        self.o2PWM.ChangeDutyCycle(0)
        print('duty_cycle_off')
        
        
        
        GPIO.output(14,GPIO.HIGH)
        GPIO.output(26,GPIO.HIGH)
 #       self.o2PWM.stop()
 #       time.sleep(1)
#        self.pPWM.stop()
        self.running = False

    def run(self):
        
        global graph,mod_val_data,control,value,ti_value,t#est
        global ti_val,pressure_support,ps_control
        global mod_val,plan,ps_change
        GPIO.output(14,GPIO.LOW)
        self.o2PWM.start(0)
        self.pPWM.start(0)
        
#        print("starting breather thread"+ str(self.o2DC)+str(self.pDC)+str(self.in_t)+str(self.out_t)+str(self.peep))
        QThread.msleep(1)
                
    

        if (mod_val == 4):
             
             print('in mode4')
 #            plan = 0
 #            graph = 1
 #            control = 1

             while self.running:
                 end = time.time()+15
                 plan = 0

                 while(time.time()<end):

                     if (mod_val_data == 1):
        #                    self.o2PWM.start(0)
       #                     self.pPWM.start(0)
                            graph = 0
                            print('compress on')
                            control = 0

                            while(test <= pressure_val):
                                self.pwm_ps_in()
                                print('pressure:',test)

                            #print('TIME',po)
                            time.sleep(1.5)    
                            self.pwm_ps_no()

                            graph = 1

                            while(test >= 8):
                                #(ti_value/4)):                           
 #                               print('exout')
                                print('pressure out:',test)

                            if(test < 8):#ti_value/4):
                                print('ti')
                                    #break
        #                    print('inmod val',test)    
                            mod_val_data =0
                            plan = 1

     
                     else:
                         graph = 1
                         control = 1
                         self.pwm_ps_out()


                
                         
                 if(plan ==0 and mod_val_data == 0):
                      print('mode changed to 1')
                      mod_val = 1
                      break
                    
           
        if (mod_val == 1 or mod_val == 2):
            print('mode 1/2 enabled')
            while self.running:
                
                self.pwm_in()
          #      print('mode 1')
                self.pwm_out()

        if (mod_val == 5):
            print('mode 5 enabled')
            while self.running:
                print('mode 5')
                self.pwm_in()
            while(self.running == False):
                    print('mode 5 off')
                    self.pwm_out()
                    break
        
               
   

    def pwm_in(self):


                global graph,i_rr,ti
                
                print("self.running.loop")
                self.start_time = time.time()
                print('start',self.start_time)
                graph = 0
                
                self.pPWM.ChangeDutyCycle(self.pressureCycleValue[0])
                self.o2PWM.ChangeDutyCycle(self.pressureCycleValue[1])
                
                GPIO.output(26,GPIO.HIGH)
                GPIO.output(14,GPIO.LOW)

                self.breathStatus = 0
                i_rr += 1

                
                             
                self._inhale_event.wait(timeout=self.in_t)
                self.end = time.time()
                if(mod_val == 1 or mod_val == 2):
                    ti = ((self.end) - (self.start_time))
                    ti = round(ti,1)
                print('ti',ti)    
    def pwm_out(self):
                global graph,peep_val,ti
                global rr_value
                self.peep = peep_val
                print('peep',peep_val)
           #     print(self.peep)
                print("pwm_out")
                
                graph = 1
                self.o2PWM.ChangeDutyCycle(self.peep)
                self.pPWM.ChangeDutyCycle(self.peep)
                print('peep',self.peep)
                GPIO.output(26,GPIO.LOW)
                self.breathStatus = 1
                self._exhale_event.wait(timeout=self.out_t)
                self.end_time = time.time()
                print('end_time',self.end_time)
                if(mod_val == 1 or mod_val == 2 ):
           #         ti = (int(self.end_time) - int(self.start_time))
                    rr_value = int(60/(int(self.end_time) - int(self.start_time)))

    def pwm_ps_out(self):
                global graph,peep_val,ti
                global rr_value             
                graph = 1
                self.o2PWM.ChangeDutyCycle(1)
                self.pPWM.ChangeDutyCycle(1)

                GPIO.output(26,GPIO.LOW)
                self.breathStatus = 1
 #               self.o2PWM.start(0)
#                self.pPWM.start(0)
    
    def pwm_ps_in(self):

                global graph,i_rr,mod_val_data
                
   #             print("self.running.loop")
                self.start_time = time.time()
   #             print('start',self.start_time)
                
                
                self.pPWM.ChangeDutyCycle(self.pressureCycleValue[0])
                self.o2PWM.ChangeDutyCycle(self.pressureCycleValue[1])
                
                GPIO.output(26,GPIO.HIGH)
                GPIO.output(14,GPIO.LOW)
                self.breathStatus = 0
                i_rr += 1

                
    def pwm_ps_no(self):
                global graph,peep_val,ti
                global rr_value
                self.peep = peep_val
                print('peep',peep_val)
           #     print(self.peep)
                print("pwm_out")
                
                graph = 1
                self.o2PWM.ChangeDutyCycle(1)
                self.pPWM.ChangeDutyCycle(1)
  #              print('peep',self.peep)
  #              GPIO.output(26,GPIO.LOW)
                self.breathStatus = 1
                
#                self.pPWM.stop()
#                self.o2PWM.stop()
#                print('compress off')
        #       self._exhale_event.wait(timeout=self.out_t)
             

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
        global gf,control
        global ini,rap,adc,ti_val,ti_value,test
        global pressure_support,pressure_val
        global firstvalue,trigger_data
        global graph,mod_val_data
        global ps_change,kz,value
        currentPressure = 0
        ko = 0
        
      #  print('getdata_init')
        read_ser = []
        pressured = []
        
#        print('getdata')
        data = [0]*4
        trigger = 2 * trigger_data
        trigger = abs(trigger)
#        print('trigger',trigger)
        endtime = time.time()+0.1
        while(time.time()<endtime):
            
            for i in range(4):
                try:  
                    data[i] = adc.read_adc(i, gain=GAIN)
           #         print('i ,data',i,data[i])
                except:
                    print('i2c error')
                
         #   data_s = data.rstrip()
         #   data_string = str(data_s)
        #    data = list(data_string.split(","))
            #sleep(0.3)
            pressurel = []
            
            pressurel.append(int(data[0])/8000)
            pressured.append(int(data[0])/8000)
   #         print('presss',pressurel)
            #time.sleep(0.5)
   #     if(graph == 2):
        
       
  #      print('sensor',data[0]/8000)
        values = sum(pressured[0:4])/len(pressured)
        value_s = ((-2.5+values)/0.2)*5
        value = int(value_s)
     #   ti_value = int(ti_val)
        
 #       if(ti_value <= value):
            
        #    print('value: ti-val:',value,ti_val)
        #    print('high')
 #       if(graph == 0 and int(ti_val)/4 >= int(values)) :
 #           print('low')
        
  
        pressurel.sort(reverse = True)
   #     print(pressurel)
    #    print('test',pressurel[0])
        
            
        if(graph == 0):
            
        #    print('Inhaling')pwm
      #      pressure_support = (int(data[0])/8000)*5
    #        print('pss',pressure_support)
            if(ini == 0):
                    firstvalue = pressurel[0]
                    print('firstvalue',firstvalue)
                    currentPressure = firstvalue
                    ini += 1
             #       print('ini',ini)
            else:
                    nextvalue = pressurel[0]
                    if(nextvalue > firstvalue):
                        currentPressure = nextvalue
                        firstvalue = currentPressure
                    if(nextvalue < firstvalue):
                        currentPressure = firstvalue
                        firstvalue = currentPressure
              #      print('cpp',currentPressure)        
            if (currentPressure < pressurel[0]):
                currentPressure = pressurel[0]
            else:
               currentPressure = firstvalue
            test1 = round(currentPressure,1)
   #         print('test',currentPressure)
       


            
       #     print('mode 4 in gra')
            

   #         print('val',value)
   #         print('ti',ti_val)
           
            ###
            '''

            if(rap == 1 and int(ti_val) < value):
          #      time.sleep(0.5)
                print('ps/change',(value))
                ps_change = 1
                time.sleep(2)
                ko = 1
                kz = 0
            if(ko ==1 and int(ti_val)/4 <= (value)):
                print('last_cal',(int(ti_val)/4))
                ps_change = 2
                time.sleep(2)
                ko = 0
            '''
            ###

 

      #      print('press_su',pressure_support)
       #     print('ps',pressure_support)
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
            press = currentPressure     
            prs = "{:.1f}".format(press)
            pr = float(prs)
     #       print('pr',pr)
            pressure = ((pr-2.5)/0.2)

     #       print('pressure',pressure)
            pressure = (round(pressure,1))
            test = pressure*5    
            self.dataDict["Dpress+"].append(pressure*5)   
        if (graph == 1):
 #           print('Exhaling')
            currentPressure = int(data[0])/8000
#            test = round(currentPressure,1)
#            print('test',currentPressure)
            
         #   print('exale pre value',currentPressure)
            if(mod_val == 4):
                time.sleep(0.5)
                if (control == 1 and currentPressure < 2.7):
                    mod_val_data = 1
                    print('pressure_low')
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
            
            press = currentPressure
#            print('min volt',currentPressure)
            prs = "{:.1f}".format(press)
            pr = float(prs)
     #       print('pr',pr)
            pressure = ((pr-2.5)/0.2)

     #       print('pressure',pressure)
            pressure = (round(pressure,1))
            test = pressure*5

            
            
            

            
            
        #    values = sum(pressured[0:4])/len(pressured)
       #     value = pressure*5
     #       print('sensor vals',value)
            
            self.dataDict["Dpress+"].append(pressure*5)
        #print('sen',data )
        self.dataDict["o2conc"].append(float(data[3])*0.1276)
#        print('datadict', self.dataDict)
 #       print('g',self.dataDict)
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
        #self.dataDict["o2conc"].append(int(data[1]))
        #self.dataDict["AirV"].append(int(data[2]))
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
        #self.dataDict["Dpress-"].append(int(data[4]))
        #self.dataDict["press+"].append(int(data[5]))
        #self.dataDict["press-"].append(int(data[6]))
        #self.dataDict["co2"].append(int(data[7]))
        #self.dataDict["temp"].append(int(data[8]))
      #  self.dataDict["hum"].append(int(data[9]))

        #if len(self.dataDict["o2conc"]) >180:
         #   self.dataDict["o2conc"].pop(0)
          #  self.dataDict["AirV"].pop(0)
           # self.dataDict["Dpress+"].pop(0)
            #self.dataDict["Dpress-"].pop(0)
            #self.dataDict["press+"].pop(0)
            #self.dataDict["press-"].pop(0)
            #self.dataDict["co2"].pop(0)
            #self.dataDict["temp"].pop(0)
            #self.dataDict["hum"].pop(0)
      
       # print('g',self.dataDict)    
        
        #return self.dataDict

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



class App(QFrame):

    def __init__(self):
        super().__init__()
        self.title = 'ventilator'
        self.pmean = []
        self.mean = []
        self.mean_v = 0
        
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 100
        self.on = 0
        
        self.initUI()
        self.ie_value = 2
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
  #      ie_pdata =2
        bpm = self.lbpm.text()
        ie_pdata = int(self.ie_value)
        print('ie-ui',self.ie_value)
        ###
        '''
        
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
 #       print('ie',ie_pdata)   
# # # # # # # # # #         print('ie'+str(ie_pdata))
        ###
        '''
        ###
        self.breathCount = 60 / int(bpm)
        print('breathcount',self.breathCount)
    
        self.inhaleTime = (self.breathCount/(ie_pdata+1)) 
        self.exhaleTime = (self.breathCount ) - self.inhaleTime
        
        print('ie',ie_pdata)        
        in_time = self.inhaleTime
        out_time = self.exhaleTime
        print('in',self.inhaleTime)
        print('out',self.exhaleTime)
        
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
        self.graphwidget.setLabel('left', 'Pressure')
        self.graphwidget.setLabel('bottom', 'Time')
        #self.graphwidget.getPlotItem().hideAxis('bottom')

        pen = pg.mkPen(color='y')
        self.data_line =  self.graphwidget.plot(self.y, pen=pen) #fillLevel=0,brush=(150,50,150,50))           #pen=pen)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()
        self.layout.addWidget(self.graphwidget,2,0,5,4)
        #self.data_line.clear()
        

    def update_plot_data(self):
        
        global data_m,rr_value,i_rr,ti,mod_val,pressure_val,pressure_pdata
        a = 0
        
        
        if self.bthThread.breathStatus == 0:
            global data_m
            #print('datarec', data_m)
            #self.data_get()
            self.lbcadata.setText('Inhale')
            #press = self.lpresd.text()
            #self.lpresd.setText(press)
            self.lbtidata.setText(str(ti))
            #self.lpbdata.setText(press)
            if (self.on == 1):
            
                vol = self.lvol.text()
                vv = int(vol)
                self.lmvd.setText(str(vv))
                volc = int(vol)
                self.lbvedata.setText(str(volc))
                if(mod_val == 2):
                    
                    self.lmvd.setText(str(pressure_val*30))
                    self.lbvedata.setText(str(pressure_val*30))
         #   peep = int(self.lpeep.text()) + randint(0,10)
            self.lbpeepdata.setText('-')

            try:
                
                self.pip = max(data_m['Dpress+'])
          #      self.mean.append(self.pip)
          #      self.pmean = self.mean[-4:]
           #     print('pmean',self.pmean)
           #     print('len',len(self.pmean))
           ###
                '''
                if (len(self.pmean)%4) == 0:
                    self.mean = self.pmean[-4:]
                    self.mean_v = sum(self.mean)/4
             #       print('mean',self.mean_v)
                    if(i_rr < 3):
                        print('i-rr',i_rr)
                        self.lbpmeandata.setText(str(self.mean_v))
                        '''
           ###

                
                if(mod_val == 2 or mod_val == 4):
                    self.pip = pressure_val
                    self.lbpdata.setText(str(self.pip))
                else:
                    self.lbpdata.setText(str(self.pip))
                    
            except:
                self.lbpdata.setText('0')
                
  
        #print('pip',self.pip)   
        if self.bthThread.breathStatus == 1:
            self.lbcadata.setText('Exhale')
            #print('datarec', data_m)
            self.lpresd.setText('0')
            self.lbtidata.setText('-')
            #self.lpbdata.setText(press)
            if(self.on == 1):
#                 vol = self.lvol.text()
        #        vv = int(vol)+int(randint(-10,15))
                self.lmvd.setText('-')
          #      volc = int(vol)+int(randint(-10,5))
                self.lbvedata.setText('-')

      #      print('pip',self.pip)
      #      print('inhale',self.inhaleTime)
      #      print('peep',self.peep)
      #      print('exhale',self.exhaleTime)
            
            try:
                self.peep_d = min(data_m['Dpress+'])
     #           print('peep',self.peep_d)
                if( self.peep_d > 2.7):
                    self.peep = "{:.1f}".format(self.peep_d)
                else:
                    self.peep = 2.7
        #        print('pmeen',pmeen)
          #      peep = (self.lpeep.setText(str(pmeen)))
                self.lbpeepdata.setText(str(self.peep))
                self.lrrd.setText(str(rr_value))
                self.mean = float((self.pip * self.inhaleTime) + (float(self.peep) * self.exhaleTime))
      #          print('mean',self.mean)
                if(ti != 0):
                    ti = float(ti)
                    self.pmean  = self.mean / ti
    #                print('pmean',self.pmean)
   #                 print('ti',ti)
                    self.pmean = "{:.1f}".format(self.pmean)
                    self.lbpmeandata.setText(str(self.pmean))
           #             print('pmean',self.pmean)
            except:
                drk = 0
            

            
        
        try:
                #self.y = self.y[1:]
                #self.y.append(int(data_m['Dpress+'][-1]))

                pressure = data_m['Dpress+'][-1] #*5
                
              #  o2s = str(data_m["o2conc"][-1])
                o2 = int(data_m["o2conc"][-1]) #"{.:2f}".format(o2s)
      #          print('o2', o2)
                o2s = "{:.1f}".format(o2)
                if(o2 > 100):
                    self.laprd.setStyleSheet("background-color: red")
                    self.laprd.setText(str(o2s))
                if(o2 < 100):
                    self.laprd.setStyleSheet("background-color: green")
                    self.laprd.setText(str(o2s))
                if(mod_val == 2 or mod_val == 4):
                   # print('in  2')
                    if(pressure > pressure_val):
                        self.lpresd.setText(str(pressure_val))
                   #     print('prd',pressure_val)
                 #       print('prrrd',pressure)
                    else:
                        self.lpresd.setText(str(pressure))
                 #       print('press',pressure)
                    
                if(mod_val == 1 or mod_val ==5):
                    self.lpresd.setText(str(pressure))
                    
                
                #print('try',data_m['Dpress+'][-1])
                #print('y',self.y)
       #         print('plvvv',pressure)
               # self.data_line.setData(self.y)
                

        except:
            drk = 1
            
            
        try:
            
                self.y = self.y[1:]
                self.y.append(int(data_m['Dpress+'][-1]))
                self.data_line.setData(self.y)
          #      print('Graph plotting')
        except:
              g = 1
        #      print('Graph error')
            
         #   print('NO sensor data recevied')

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
           #     print('default')
        
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
              
                
    #    print("Data type before reconstruction : ", type(data))

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
        Bstart.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        Bstart.clicked.connect(self.on_process)
        self.layout.addWidget(Bstart,1,6)
        Bstart.clicked.connect(self.stop)

        
        
    def stop(self):
        self.bstop = QPushButton('stop')
        self.bstop.setFont(QFont('Arial', 15))
        self.bstop.setStyleSheet("background-color: grey")
        self.bstop.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.layout.addWidget(self.bstop,1,6)
        self.bstop.clicked.connect(self.off_process)
        self.bstop.clicked.connect(self.stop_action)
        
    def vc(self):
        global pressure_val
        
        self.label_reset()
        self.readSettings(1)
        
        self.lpressure.setText(str(self.settings["pressure"]["default"]))
        pressure_val = int(self.lpressure.text())
        self.lpresd.setVisible(False)

        self.lvol.setText(str(self.settings["volume"]["default"]))
        self.lbpm.setText(str(self.settings["bpm"]["default"]))
        self.lpeep.setText(str(self.settings["peep"]["default"]))
        self.lfio2.setText(str(self.settings["fio2"]["default"]))    
    def ps(self):
        global pressure_val
        
        self.label_reset()
        self.readSettings(1)
        self.lpressure.setText(str(self.settings["pressure"]["default"]))
        pressure_val = int(self.lpressure.text())

        self.lvol.setText(str(self.settings["volume"]["default"]))
        self.lbpm.setText(str(self.settings["bpm"]["default"]))
        self.lpeep.setText(str(self.settings["peep"]["default"]))
        self.lfio2.setText(str(self.settings["fio2"]["default"]))
        
    def hfonc(self):
        self.label_reset()
        self.readSettings(2)
        self.Bti.setVisible(False)
        self.lpressure.setText(str(self.settings["pressure"]["default"]))
        self.lvol.setText(str(self.settings["volume"]["default"]))
        self.lbpm.setText(str(self.settings["bpm"]["default"]))
        self.lpeep.setText(str(self.settings["peep"]["default"]))
        self.lfio2.setText(str(self.settings["fio2"]["default"]))
        
    def pc(self):
        self.label_reset()
        self.readSettings(1)
        self.lpresd.setVisible(True)
        self.Bti.setVisible(False)
        self.Bvol.setEnabled(False)
        self.lvol.setVisible(False)
        self.Bpressure.setEnabled(True)
        self.lpressure.setVisible(True)
        self.lpressure.setText(str(self.settings["pressure"]["default"]))
        self.lvol.setText(str(self.settings["volume"]["default"]))
        self.lbpm.setText(str(self.settings["bpm"]["default"]))
        self.lpeep.setText(str(self.settings["peep"]["default"]))
        self.lfio2.setText(str(self.settings["fio2"]["default"]))
        
    def pressure_set(self):
        global mod_val

       
        self.slp = QSlider(Qt.Vertical, self)
        self.slp.setStyleSheet("QSlider{min-width: 100px; max-width: 100px;} QSlider::groove:vertical{border: 1px solid #262626; width: 30px; background: grey; margin: 0 12px;} QSlider::handle:vertical {background: white; border: 2px #55F4A5; width: 40px; height: 50px; line-height: 20px;margin-top: -4px; margin-bottom: -4px; border-radius: 9px;}") 
        
        if(mod_val == 4):
            self.slp.setRange(0, 32)
        else:
            self.slp.setRange(0, 50)
            
        self.slp.setFocusPolicy(Qt.StrongFocus)
        self.slp.setPageStep(1)
        v = self.lpressure.text()
        self.slp.setValue(int(v))
        self.slp.valueChanged.connect(self.pupdateLabel)
        self.slp.setTickPosition(QSlider.TicksBelow)
        self.slp.setTickInterval(5)

        self.plabel = QLabel(v, self)
        self.plabel.setAlignment(Qt.AlignRight | Qt.AlignRight)
        self.plabel.setMinimumWidth(80)
        self.plabel.setFont(QFont('Arial', 25))
        self.plabel.setStyleSheet("color: white;  background-color: black")

        self.layout.addWidget( self.slp,2,6,4,1,alignment=Qt.AlignRight)
        self.layout.addWidget(self.plabel,6,6)
        

        self.pupdate_val = QPushButton('P update')
        self.pupdate_val.setFont(QFont('Verdana', 13))  
        self.pupdate_val.setStyleSheet("background-color: orange")
        self.layout.addWidget(self.pupdate_val,7,6)
        self.pupdate_val.clicked.connect(self.update_setp)
        
    def update_setp(self):
        global pressure_val

       # self.update_parameters()
        try:
            self.lpressure.setText(self.pressure_values)
        except:
            v = self.plabel.text()
            self.lpressure.setText(v)
           
        pressure_val = int(self.lpressure.text())
        self.slp.deleteLater()
        self.plabel.deleteLater()
        self.pupdate_val.deleteLater()
    def pupdateLabel(self, value):      
        self.plabel.setText(str(value))       
        self.pressure_values = self.plabel.text()

    def bpm_set(self):

        self.slbpm = QSlider(Qt.Vertical, self) 
        self.slbpm.setRange(0, 20)
        self.slbpm.setStyleSheet("QSlider{min-width: 100px; max-width: 100px;} QSlider::groove:vertical{border: 1px solid #262626; width: 30px; background: grey; margin: 0 12px;} QSlider::handle:vertical {background: white; border: 2px #55F4A5; width: 40px; height: 50px; line-height: 20px;margin-top: -4px; margin-bottom: -4px; border-radius: 9px;}") 
        v = int(self.lbpm.text())
        self.slbpm.setValue(v)
        self.slbpm.setFocusPolicy(Qt.StrongFocus)
        self.slbpm.setPageStep(5)
        self.slbpm.valueChanged.connect(self.bpmupdateLabel)
        self.slbpm.setTickPosition(QSlider.TicksBelow)
        self.slbpm.setTickInterval(5)

        self.bpmlabel = QLabel(str(v), self)
        self.bpmlabel.setAlignment(Qt.AlignRight | Qt.AlignRight)
        self.bpmlabel.setMinimumWidth(80)
        self.bpmlabel.setFont(QFont('Arial', 25))
        self.bpmlabel.setStyleSheet("color: white;  background-color: black")

        self.layout.addWidget( self.slbpm,2,6,4,1,alignment=Qt.AlignRight)
        self.layout.addWidget(self.bpmlabel,6,6)
        

        self.bupdate_val = QPushButton('BPM update')
        self.bupdate_val.setFont(QFont('Verdana', 13))  
        self.bupdate_val.setStyleSheet("background-color: orange")
        self.layout.addWidget(self.bupdate_val,7,6)
        self.bupdate_val.clicked.connect(self.update_setbpm)
        
    def update_setbpm(self):      

        try:
            self.lbpm.setText(self.bpm_v)
        except:    
            v = self.bpmlabel.text()
            self.lbpm.setText(v)
        self.slbpm.deleteLater()
        self.bpmlabel.deleteLater()
        self.bupdate_val.deleteLater()    
        #self.update_parameters()
    
    def bpmupdateLabel(self, value):      
        self.bpmlabel.setText(str(value))
        #self.lbpm.setText(str(value))
        self.bpm_v = str(value)     

    def peep_set(self):

        self.slpeep = QSlider(Qt.Vertical, self) 
        self.slpeep.setRange(0, 20)
        self.slpeep.setStyleSheet("QSlider{min-width: 100px; max-width: 100px;} QSlider::groove:vertical{border: 1px solid #262626; width: 30px; background: grey; margin: 0 12px;} QSlider::handle:vertical {background: white; border: 2px #55F4A5; width: 40px; height: 50px; line-height: 20px;margin-top: -4px; margin-bottom: -4px; border-radius: 9px;}") 
        v = self.lpeep.text()
        self.slpeep.setValue(int(v))
        self.slpeep.setFocusPolicy(Qt.StrongFocus)
        self.slpeep.setPageStep(5)
        self.slpeep.valueChanged.connect(self.peepupdateLabel)
        self.slpeep.setTickPosition(QSlider.TicksBelow)
        self.slpeep.setTickInterval(5)

        self.peeplabel = QLabel(v, self)
        self.peeplabel.setAlignment(Qt.AlignRight | Qt.AlignRight)
        self.peeplabel.setMinimumWidth(80)
        self.peeplabel.setFont(QFont('Arial', 25))
        self.peeplabel.setStyleSheet("color: white;  background-color: black")

        self.layout.addWidget( self.slpeep,2,6,4,1,alignment=Qt.AlignRight)
        self.layout.addWidget(self.peeplabel,6,6)
        
        #self.peeplabel = QLabel('Vol update', self)
        #self.peeplabel.setAlignment(Qt.AlignRight | Qt.AlignRight)
       # self.peeplabel.setMinimumWidth(80)
       # self.peeplabel.setFont(QFont('Arial', 10))
       # self.peeplabel.setStyleSheet("color: white;  background-color: black")
       # self.layout.addWidget(self.peeplabel,7,6)

        self.peepupdate_val = QPushButton('peep update')
        self.peepupdate_val.setFont(QFont('Verdana', 13))  
        self.peepupdate_val.setStyleSheet("background-color: orange")
        self.layout.addWidget(self.peepupdate_val,7,6)
        self.peepupdate_val.clicked.connect(self.update_setpeep)
        
    def update_setpeep(self):
        global peep_val
        try:
            self.lpeep.setText(self.peep_v)
        except:
            v = self.peeplabel.text()
            self.lpeep.setText(v)
        peep_val = int(self.lpeep.text())
        #print('ui_peep',peep_val)
        self.slpeep.deleteLater()
        self.peeplabel.deleteLater()
        self.peepupdate_val.deleteLater()
        #self.update_parameters()
    
    def peepupdateLabel(self, value):
        
        self.peeplabel.setText(str(value)) 
        self.peep_v = str(value)
        
    def ti_set(self):

        self.slti = QSlider(Qt.Vertical, self) 
        self.slti.setRange(0, 100)
        self.slti.setStyleSheet("QSlider{min-width: 100px; max-width: 100px;} QSlider::groove:vertical{border: 1px solid #262626; width: 30px; background: grey; margin: 0 12px;} QSlider::handle:vertical {background: white; border: 2px #55F4A5; width: 40px; height: 50px; line-height: 20px;margin-top: -4px; margin-bottom: -4px; border-radius: 9px;}") 
        self.slti.setFocusPolicy(Qt.StrongFocus)
        v = self.ti.text()
        self.slti.setValue(int(v))
        self.slti.setPageStep(5)
        self.slti.valueChanged.connect(self.tiupdateLabel)
        self.slti.setTickPosition(QSlider.TicksBelow)
        self.slti.setTickInterval(5)

        self.tilabel = QLabel(v, self)
        self.tilabel.setAlignment(Qt.AlignRight | Qt.AlignRight)
        self.tilabel.setMinimumWidth(80)
        self.tilabel.setFont(QFont('Arial', 25))
        self.tilabel.setStyleSheet("color: white;  background-color: black")

        self.layout.addWidget( self.slti,2,6,4,1,alignment=Qt.AlignRight)
        self.layout.addWidget(self.tilabel,6,6)

        self.tiupdate_val = QPushButton('ti update')
        self.tiupdate_val.setFont(QFont('Verdana', 10))  
        self.tiupdate_val.setStyleSheet("background-color: orange")
        self.layout.addWidget(self.tiupdate_val,7,6)
        self.tiupdate_val.clicked.connect(self.update_setti)
        
    def update_setti(self):
        global ti_val
        try:
            self.ti.setText(self.ti_v)
        except:
            v = self.tilabel.text()
            self.lfio2.setText(v)
        ti_val = self.ti.text()
        self.slti.deleteLater()
        self.tilabel.deleteLater()
        self.tiupdate_val.deleteLater()
        #self.update_parameters()
    
    def tiupdateLabel(self, value):      
        self.tilabel.setText(str(value))
        #self.lfio2.setText(str(value))
        self.ti_v = str(value)     
        

    def fio2_set(self):

        self.slfio2 = QSlider(Qt.Vertical, self) 
        self.slfio2.setRange(0, 100)
        self.slfio2.setStyleSheet("QSlider{min-width: 100px; max-width: 100px;} QSlider::groove:vertical{border: 1px solid #262626; width: 30px; background: grey; margin: 0 12px;} QSlider::handle:vertical {background: white; border: 2px #55F4A5; width: 40px; height: 50px; line-height: 20px;margin-top: -4px; margin-bottom: -4px; border-radius: 9px;}") 
        self.slfio2.setFocusPolicy(Qt.StrongFocus)
        v = self.lfio2.text()
        self.slfio2.setValue(int(v))
        self.slfio2.setPageStep(5)
        self.slfio2.valueChanged.connect(self.fio2updateLabel)
        self.slfio2.setTickPosition(QSlider.TicksBelow)
        self.slfio2.setTickInterval(5)

        self.fio2label = QLabel(v, self)
        self.fio2label.setAlignment(Qt.AlignRight | Qt.AlignRight)
        self.fio2label.setMinimumWidth(80)
        self.fio2label.setFont(QFont('Arial', 25))
        self.fio2label.setStyleSheet("color: white;  background-color: black")

        self.layout.addWidget( self.slfio2,2,6,4,1,alignment=Qt.AlignRight)
        self.layout.addWidget(self.fio2label,6,6)

        self.fupdate_val = QPushButton('fio2 update')
        self.fupdate_val.setFont(QFont('Verdana', 10))  
        self.fupdate_val.setStyleSheet("background-color: orange")
        self.layout.addWidget(self.fupdate_val,7,6)
        self.fupdate_val.clicked.connect(self.update_setfio2)
        
    def update_setfio2(self):
        global fio_val
        try:
            self.lfio2.setText(self.fio2_v)
        except:
            v = self.fio2label.text()
            self.lfio2.setText(v)
        fio_val = self.lfio2.text()
        self.slfio2.deleteLater()
        self.fio2label.deleteLater()
        self.fupdate_val.deleteLater()
        #self.update_parameters()
    
    def fio2updateLabel(self, value):      
        self.fio2label.setText(str(value))
        #self.lfio2.setText(str(value))
        self.fio2_v = str(value)     
        
    def value_set(self):
       
        self.sl = QSlider(Qt.Vertical, self) 
        self.sl.setRange(0, 100)
        self.sl.setStyleSheet("QSlider{min-width: 100px; max-width: 100px;} QSlider::groove:vertical{border: 1px solid #262626; width: 30px; background: grey; margin: 0 12px;} QSlider::handle:vertical {background: white; border: 2px #55F4A5; width: 40px; height: 50px; line-height: 20px;margin-top: -4px; margin-bottom: -4px; border-radius: 9px;}") 
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
        self.slv.setRange(50, 1500)
        self.slv.setStyleSheet("QSlider{min-width: 100px; max-width: 100px;} QSlider::groove:vertical{border: 1px solid #262626; width: 30px; background: grey; margin: 0 12px;} QSlider::handle:vertical {background: white; border: 2px #55F4A5; width: 40px; height: 50px; line-height: 20px;margin-top: -4px; margin-bottom: -4px; border-radius: 9px;}") 
        self.slv.setFocusPolicy(Qt.NoFocus)
        v = self.lvol.text()
        self.slv.setValue(int(v))
        self.slv.setPageStep(5)
        self.slv.setGeometry(QtCore.QRect(390,300,360,36))
        self.slv.valueChanged.connect(self.volume_update)
        self.slv.setTickPosition(QSlider.TicksBelow)
        self.slv.setTickInterval(5)

        self.vlabel = QLabel(v, self)
        self.vlabel.setAlignment(Qt.AlignRight | Qt.AlignRight)
        self.vlabel.setMinimumWidth(80)
        self.vlabel.setFont(QFont('Arial', 25))
        self.vlabel.setStyleSheet("color: white;  background-color: black")

        self.layout.addWidget( self.slv,2,6,4,1,alignment=Qt.AlignRight)
        self.layout.addWidget(self.vlabel,6,6)

        self.vupdate_val = QPushButton('Vol update')
        self.vupdate_val.setFont(QFont('Arial', 13))  
        self.vupdate_val.setStyleSheet("background-color: red")
        self.layout.addWidget(self.vupdate_val,7,6)
        self.vupdate_val.clicked.connect(self.lvolume_set)
        
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
    
        
    def volume_update(self, value):
        self.vlabel.setText(str(value))
        self.vol_v = str(value)
        
    def lvolume_set(self):
        global volume_val
        #print(self.updated_value) #Updated value
        try:
            self.lvol.setText(self.vol_v)
        except:
            v = self.vlabel.text()
            self.lvol.setText(v)
        volume_val = self.lvol.text()
        self.slv.deleteLater()
        self.vlabel.deleteLater()
        self.vupdate_val.deleteLater()
        self.update_parameters()
    
    def bpm_update(self):
        self.bpm_value = True

    def fio2_update(self):
        self.fio2_value = True

    def peep_update(self):
        self.peep_value = True    

    def pressure_update(self):
        self.pressure_value = True

    def volume_updates(self):
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
      self.layout.addWidget(self.cb,7,4)
      self.cb.currentIndexChanged.connect(self.ie_updated)

    def ie_updated(self, value):
        #self.cb.deleteLater()
        self.ie_value = str(value)
   #     print('iev',self.ie_value)
        if(value == 1):
            self.lbrdata.setText("1:1")
        if(value == 2):
            self.lbrdata.setText("1:2")
        if(value == 3):
            self.lbrdata.setText("1:3")
        if(value == 4):
            self.lbrdata.setText("1:4")    
        
                

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
      self.cbtr.setFont(QFont('Arial', 10))
      self.cbtr.setStyleSheet("color: black;  background-color: white") 
      self.cbtr.setGeometry(200, 150, 120, 40)  
      self.layout.addWidget(self.cbtr,5,4)
      self.cbtr.currentIndexChanged.connect(self.trigger_updated)

    def trigger_updated(self, value):
        #self.cbtr.deleteLater()
                                        
        global trigger_data
        if value == 1:
            trigger_data = -10
        if value == 2:
            trigger_data = -9
        if value == 3:
            trigger_data = -8
        if value == 4:
            trigger_data = -7
        if value == 5:
            trigger_data = -6
        if value == 6:
            trigger_data = -5
        if value == 7:
            trigger_data = -4
        if value == 8:
            trigger_data = -3    
        #trigger_data = int(self.ltrigger.text())
#        print('t_da8a',trigger_data)                                
        #print(self.trigger_value)
        #print(trigger_data)

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
      self.layout.addWidget(self.md,3,4)
      self.md.currentIndexChanged.connect(self.mode_updated)

    def mode_updated(self, value):
        global mod_val
        #self.md.deleteLater()
        self.mode_set = str(value)
        if self.mode_set == '1':
         #   self.lmode.setText('None')
            mod_val = 1
            self.Bpressure.setEnabled(True)
            self.lpressure.setVisible(True)
            self.Bti.setVisible(False)
            self.Bvol.setEnabled(True)
            self.lvol.setVisible(True)
            self.Bbpm.setEnabled(True)
            self.lbpm.setVisible(True)
            self.Bpeep.setEnabled(True)
            self.lpeep.setVisible(True)               
            self.Bpressure.setText('Pressure')
  #          print('mode_val',mod_val)
        if self.mode_set == '2':
          #  self.lmode.setText('VC')
            
            mod_val = 1
            self.Bpressure.setEnabled(False)
            self.lpressure.setVisible(False)
            self.Bti.setVisible(False)
            self.Bvol.setEnabled(True)
            self.lvol.setVisible(True)
            self.Bbpm.setEnabled(True)
            self.lbpm.setVisible(True)
            self.Bpeep.setEnabled(True)
            self.lpeep.setVisible(True)            
            self.Bpressure.setText('Pressure')
            self.vc()
     #       print('mode_val',mod_val)
        if self.mode_set == '3':
           # self.lmode.setText('PC')
            mod_val = 2
            self.Bpressure.setText('Ps')
      #      print('mode_val',mod_val)
            self.pc()
        if self.mode_set == '4':
            self.ps()
            #self.lmode.setText('SPONT+PS')
            mod_val = 4
            self.Bpressure.setEnabled(True)
            self.lpressure.setVisible(True)
            self.Bti.setVisible(False)
            self.Bvol.setEnabled(False)
            self.lvol.setVisible(False)
            self.Bbpm.setEnabled(True)
            self.lbpm.setVisible(True)
            self.Bpeep.setEnabled(True)
            self.lpeep.setVisible(True)
            self.Bpressure.setText('PS')
            self.lmvd.setText('-')
            self.lbvedata.setText('0')
            self.lbvedata.setText('0')
   #         print('mode_val',mod_v''al)
        if self.mode_set == '5':
            self.hfonc()
            #self.lmode.setText('HFONC')
            mod_val = 5
            self.Bpressure.setEnabled(False)
            self.lpressure.setVisible(False)
            self.Bti.setVisible(False)
            self.Bvol.setEnabled(False)
            self.lvol.setVisible(False)
            self.Bbpm.setEnabled(False)
            self.lbpm.setVisible(False)
            self.Bpeep.setEnabled(False)
            self.lpeep.setVisible(False)
            self.Bpressure.setText('Pressure')
     #       print('mode_val',mod_val)
        if self.mode_set == '6':
            #self.lmode.setText('BiPAP')
            mod_val = 4
            self.lpressure.setVisible(True)
            self.Bti.setVisible(False)
            self.Bvol.setEnabled(False)
            self.lvol.setVisible(False)
            self.Bbpm.setEnabled(True)
            self.lbpm.setVisible(True)
            self.Bpeep.setEnabled(True)
            self.lpeep.setVisible(True)
            self.Bpressure.setText('PS')
            self.lmvd.setText('-')
            self.lbvedata.setText('0')
            self.lbvedata.setText('0')
            self.Bpressure.setText('PS')
     #       print('mode_val',mod_val)
    def on_process(self):
   #     print("pressed start button")
    #    dataFetched = self.fetchData()
    #    self.beThread.dataUpdate = dataFetched
        self.fetch_data()
        self.bthThread.update_pwm_Data()
        self.beThread.running = True
        self.bthThread.running = True
  #      self.disableUI()
        self.beThread.start()
        self.bthThread.start()
        self.on = 1
        
    def off_process(self):
  #      print("pressed stop button")

        self.on = 0
        self.beThread.stopSignal.emit()
        self.bthThread.stopSignal.emit()
        GPIO.output(14,GPIO.HIGH)
        GPIO.output(26,GPIO.HIGH)
        
   #     print('closed')
        
    def createGridLayout(self):
        global lpressure
        global pressure_val,volume_val,fio_val,peep_val
        self.horizontalGroupBox = QGroupBox() 
        self.layout = QGridLayout()
        self.layout.setColumnStretch(6, 9)
        self.layout.setColumnStretch(6, 9)     

        #Adding push buttons
        self.Bpressure = QPushButton('Pressure') #pressurepush button
        self.Bpressure.setGeometry(0, 0, 100, 40)
        self.Bpressure.setFont(QFont('Arial', 15))  
        self.Bpressure.setStyleSheet("background-color: white")
        self.Bpressure.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.layout.addWidget(self.Bpressure,8,0)
        
        self.Rgraph = QPushButton('Refresh Graph') #GraphRefreshbutton
        self.Rgraph.setGeometry(0, 0, 100, 40)
        self.Rgraph.setFont(QFont('Arial', 15))  
        self.Rgraph.setStyleSheet("background-color: white")
        self.Rgraph.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.layout.addWidget(self.Rgraph,7,0)
        self.Rgraph.clicked.connect(self.graph)
        
        self.Bpressure.clicked.connect(self.pressure_set)
        self.Bpressure.clicked.connect(self.pressure_update)

        self.lpressure = QLabel("0")  #pressure label
        self.lpressure.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lpressure.setFont(QFont('Arial', 15))
        self.lpressure.setStyleSheet("color: white;  background-color: black")
 #       
        a = str(self.settings["pressure"]["default"])
        self.lpressure.setText(a)
        pressure_val = int(self.lpressure.text())
        self.layout.addWidget(self.lpressure,9,0)
        
        self.Bvol = QPushButton('Volume') #volumePushButton
        self.Bvol.setGeometry(0, 0, 100, 40)
        self.Bvol.setFont(QFont('Arial', 15))
        self.Bvol.setStyleSheet("background-color: white")
        self.Bvol.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.layout.addWidget(self.Bvol,8,1)
        #Bvol.clicked.connect(self.volume_update)
        self.Bvol.clicked.connect(self.volume_set)
        
        
        self.lvol = QLabel("0")  #volume label
        self.lvol.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lvol.setFont(QFont('Arial', 15))
        self.lvol.setStyleSheet("color: white;  background-color: black")
        a = str(self.settings["volume"]["default"])
        self.lvol.setText(a)
        volume_val = int(self.lvol.text())
        self.layout.addWidget(self.lvol,9,1)
  
        self.Bbpm = QPushButton('BPM')  #BPM PushButton
        self.Bbpm.setGeometry(0, 0, 100, 40)
        self.Bbpm.setFont(QFont('Arial', 15))
        self.Bbpm.setStyleSheet("background-color: white")
        self.Bbpm.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.layout.addWidget(self.Bbpm,8,2)
        self.Bbpm.clicked.connect(self.bpm_set)
        self.Bbpm.clicked.connect(self.bpm_update)

        self.lbpm = QLabel("0")  #BPM label
        self.lbpm.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lbpm.setFont(QFont('Arial', 15))
        self.lbpm.setStyleSheet("color: white;  background-color: black")
        a = str(self.settings["bpm"]["default"])
        self.lbpm.setText(a)
        self.layout.addWidget(self.lbpm,9,2)

        self.Bpeep = QPushButton('PEEP')  #peep_button
        self.Bpeep.setGeometry(0, 0, 100, 40)
        self.Bpeep.setFont(QFont('Arial', 15))  
        self.Bpeep.setStyleSheet("background-color: white")
        self.Bpeep.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.layout.addWidget(self.Bpeep,8,3)
        self.Bpeep.clicked.connect(self.peep_set)
        self.Bpeep.clicked.connect(self.peep_update)

        self.lpeep = QLabel("0")  #peep label
        self.lpeep.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lpeep.setFont(QFont('Arial', 15))
        self.lpeep.setStyleSheet("color: white;  background-color: black")
        a = str(self.settings["peep"]["default"])
        self.lpeep.setText(a)
        peep_val = int(self.lpeep.text())
        self.layout.addWidget(self.lpeep,9,3)

        Bfio2 = QPushButton('fio2')  #fio2 Button
        Bfio2.setGeometry(0, 0, 100, 40)
        Bfio2.setFont(QFont('Arial', 15))
        Bfio2.setStyleSheet("background-color: white")
        Bfio2.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.layout.addWidget(Bfio2,8,4)
        Bfio2.clicked.connect(self.fio2_set)
        Bfio2.clicked.connect(self.fio2_update)
#        Bfio2.clicked.connect(self.graph)

        self.lfio2 = QLabel("0")  #fio2 label
        self.lfio2.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lfio2.setFont(QFont('Arial', 15))
        self.lfio2.setStyleSheet("color: white;  background-color: black")
        a = str(self.settings["fio2"]["default"])
        self.lfio2.setText(a)
        fio_val = int(self.lfio2.text())
        self.layout.addWidget(self.lfio2,9,4)
        
        self.Bti = QPushButton('Ti')  #ti Button
        self.Bti.setGeometry(0, 0, 100, 40)
        self.Bti.setFont(QFont('Arial', 15))
        self.Bti.setStyleSheet("background-color: white")
        self.Bti.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.layout.addWidget(self.Bti,8,5)
        self.Bti.clicked.connect(self.ti_set)
        self.Bti.setEnabled(False)
        #Bti.clicked.connect(self.ti_update)

        self.ti = QLabel("0")  #ti label
        self.ti.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.ti.setFont(QFont('Arial', 15))
        self.ti.setStyleSheet("color: white;  background-color: black")
        #a = str(self.settings["fio2"]["default"])
        #self.lfio2.setText(a)
        #io_val = int(self.lfio2.text())
        self.layout.addWidget(self.ti,9,5)

        Bmode = QPushButton('Mode') #mode button
        Bmode.setGeometry(0, 0, 100, 400)
        Bmode.setFont(QFont('Arial', 15))
        Bmode.setStyleSheet("background-color: white")
        #self.layout.addWidget(Bmode,3,4)
        self.mode_update()
        #Bmode.clicked.connect(self.mode_update)

        Btrigger = QPushButton('Trigger')  #trigger button
        Btrigger.setGeometry(0, 0, 100, 40)
        Btrigger.setFont(QFont('Arial', 15))
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
        self.BIE.setFont(QFont('Arial', 15))
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

        ratio = '1:2'                  #breath ratio label
        lbr = QLabel('Breath Ratio')
        lbr.setFont(QFont('Arial', 15))
        self.lbrdata = QLabel(ratio)
        self.lbrdata.setFont(QFont('Arial', 25))
        lbr.setStyleSheet("color: white;  background-color: black")
        self.lbrdata.setStyleSheet("color: white;  background-color: black; border: 2px white")
        lbr.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lbrdata.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(lbr,2,5)
        self.layout.addWidget(self.lbrdata,3,5)

        pip = '0'                      #pip label       
        lbP = QLabel('PIP')
        lbP.setFont(QFont('Arial', 15))
        self.lbpdata = QLabel(pip)
        self.lbpdata.setFont(QFont('Arial', 25))
        lbP.setStyleSheet("color: #55F4A5;  background-color: black")
        self.lbpdata.setStyleSheet("color: #55F4A5;  background-color: black")
        lbP.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lbpdata.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(lbP,4,5)
        self.layout.addWidget(self.lbpdata,5,5)

        pmean = '0'                      #mean label    
        lbpmean = QLabel('P Mean')
        lbpmean.setFont(QFont('Arial', 15))
        self.lbpmeandata = QLabel(pmean)
        self.lbpmeandata.setFont(QFont('Arial', 25))
        lbpmean.setStyleSheet("color: white;  background-color: black")
        self.lbpmeandata.setStyleSheet("color: white;  background-color: black")
        lbpmean.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lbpmeandata.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(lbpmean,6,5)
        self.layout.addWidget(self.lbpmeandata,7,5)

        ti = '0'                          #Ti label
        lbti = QLabel('Ti')
        lbti.setFont(QFont('Arial', 15))
        self.lbtidata = QLabel(ti)
        self.lbtidata.setFont(QFont('Arial', 25))
        lbti.setStyleSheet("color: #55F4A5;  background-color: black")
        self.lbtidata.setStyleSheet("color: #55F4A5;  background-color: black")
        lbti.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lbtidata.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(lbti,2,6)
        self.layout.addWidget(self.lbtidata,3,6)

        ca = 'Exhale'                      #current activity label
        lbca = QLabel('Current Activity')
        lbca.setFont(QFont('Arial', 15))
        self.lbcadata = QLabel(ca)
        self.lbcadata.setFont(QFont('Arial', 15))
        lbca.setStyleSheet("color: #55F4A5;  background-color: black")
        self.lbcadata.setStyleSheet("color: #55F4A5;  background-color: black")
        lbca.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lbcadata.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        #self.layout.addWidget(lbca,2,6)
        #self.layout.addWidget(self.lbcadata,3,6)

        Ve = '0'                           #Ve label
        lbve = QLabel('VTi')
        lbve.setFont(QFont('Arial', 15))
        self.lbvedata = QLabel(Ve)
        self.lbvedata.setFont(QFont('Arial', 20))
        lbve.setStyleSheet("color: white;  background-color: black")
        self.lbvedata.setStyleSheet("color: white;  background-color: black")
        lbve.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lbvedata.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(lbve,4,6)
        self.layout.addWidget(self.lbvedata,5,6)

        rr = '0'                            #mV label
        lbrr = QLabel('mV')
        lbrr.setFont(QFont('Arial', 15))
        self.lbrrdata = QLabel(rr)
        self.lbrrdata.setFont(QFont('Arial', 20))
        lbrr.setStyleSheet("color: #55F4A5;  background-color: black")
        self.lbrrdata.setStyleSheet("color: #55F4A5;  background-color: black")
        lbrr.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lbrrdata.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(lbrr,6,6)
        self.layout.addWidget(self.lbrrdata,7,6)

        peep = '0'                            #PEEP label
        lbpeep = QLabel('PEEP')
        lbpeep.setFont(QFont('Arial', 15))
        self.lbpeepdata = QLabel(peep)
        self.lbpeepdata.setFont(QFont('Arial', 20))
        lbpeep.setStyleSheet("color: white;  background-color: black")
        self.lbpeepdata.setStyleSheet("color: white;  background-color: black")
        lbpeep.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lbpeepdata.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(lbpeep,8,6)
        self.layout.addWidget(self.lbpeepdata,9,6)
      
        Bstart = QPushButton('Start')          #start button
        Bstart.setFont(QFont('Arial', 15))
        Bstart.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        #Bstart.setStyleSheet("border-style: outset")
        #Bstart.setStyleSheet("border-colour: black")
        #Bstart.setStyleSheet("padding: 4px")
        Bstart.clicked.connect(self.on_process)
        self.layout.addWidget(Bstart,1,6)
        Bstart.clicked.connect(self.stop)
        
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

        self.lapr = QLabel('O2 %')
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

        self.lmv = QLabel('VTe')
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
        #self.layout.addWidget(self.llogo,9,0) 
  
        
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

