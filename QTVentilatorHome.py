#ventilator project
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSlot,pyqtSignal
from PyQt5.QtCore import Qt
from random import randint
from pyky040 import pyky040
from PyQt5.QtCore import QThread
from SensorCalibration import Calibration

import pyqtgraph as pg
import sys  
import os
import json
import serial
import time
import numpy as np
import Adafruit_ADS1x15
import sys
import threading
import RPi.GPIO as GPIO

global pressure_pdata
global fio2_pdata
global ex_time
global rr_value,test_ex
global ti
global check
global plan,lavs,ie_value
global pressure_support
global pressure_val,volume_val,fio_val,peep_val
global in_time,out_time
global graph
global mod_val,mod_val_data
global emergency,es
global adc
global currentPo,Slide,Hp,Hv,HP_catch
global trigger_data
global data_m,control,ti_value


global es
global comp_on
global slider
global pressure_voltage

global set_ventilator
set_ventilator  =  []
set_ventilator = sys.argv[-1]
print("set_ventilator",set_ventilator)
if set_ventilator == "icu":
    set_ventilator = 1
else:
    set_ventilator = 0
print("set_ventilator",set_ventilator)    
calibration = Calibration()
pressure_voltage = calibration.pressure_calibration()
oxygen_voltage = calibration.oxygen_calibration()
sys.setrecursionlimit(10**3)
GPIO.setmode(GPIO.BCM)                          #Setting_up_GPIO
adc = Adafruit_ADS1x15.ADS1115(address=0x48)    #Giving_instance_for_ADC

check = 0
ti = 0
lavs = 0
plan = 0
rr_value = 0
graph = 0
emergency = 0
HP_catch=0
mod_val_data = 0
control = 0
Slide = 0
currentPo = 0
Hp = 0
Hv = 0
slider = 0

ex_time = 1.5
ie_value = 2
test_ex = 4
GAIN = 1
peep_val = 4
es = 7
mod_val = 2
trigger_data = -3


def start_up():
    global comp_on

    GPIO.setup(12, GPIO.OUT)
    GPIO.setup(13, GPIO.OUT)
    time.sleep(1)
    o2PWM = GPIO.PWM(12, 100)
    pPWM = GPIO.PWM(13, 100)
    o2PWM.start(0)
    pPWM.start(0)

    time.sleep(0.1)
  
    for i in range(0,91,5):
       
        pPWM.ChangeDutyCycle(i)
        o2PWM.ChangeDutyCycle(i)
        time.sleep(0.05)
    data = adc.read_adc(0, gain=1)
    data = data/8000
    data = round(data,1)
    print('adc_val',data)
    if(data > 2.8):
        comp_on = True
    else:
        comp_on = False      

    o2PWM.stop()
    pPWM.stop()
    
start_up()    

class breathWorker(QThread):
    
    global graph

    stopSignal = pyqtSignal()
    running = False
    breathStatus = 0   
    pressureCycleValue = 0


    def __init__(self):
        super().__init__()

        self._exhale_event = threading.Event()
        self._inhale_event = threading.Event()

        GPIO.setup(12, GPIO.OUT)
        GPIO.setup(13, GPIO.OUT)
        
        GPIO.setup(14, GPIO.OUT)
        GPIO.setup(19, GPIO.OUT)
        GPIO.setup(26, GPIO.OUT)
        GPIO.output(14,GPIO.HIGH)
        
        self.o2PWM = GPIO.PWM(12, 50)
        self.pPWM = GPIO.PWM(13, 50)

    
            #mod_val    modes
            #2            volume control (vc)
            #3            pressure control (pc)
            #4            spontaneous(sp)
            #5            hfonc
            #6|4          bipap ~ sp  
    
    def update_pwm_Data(self):
        
        global pressure_val,volume_val,fio_val,mod_val
        global in_time,out_time
        global bpm_val,ie_value
        global set_ventilator

        bpm = bpm_val
        ie_pdata = int(ie_value)
        breathCount = 60 / int(bpm)
 
        inhaleTime = (breathCount/(ie_pdata+1)) 
        exhaleTime = (breathCount ) - inhaleTime
        
        in_time = inhaleTime
        out_time = exhaleTime

        pressure_pdata = int(pressure_val)
        fio2_data = int(fio_val)

        if mod_val == 2:
            volume_pdata = int(volume_val)
        elif mod_val == 5:
            volume_pdata = pressure_pdata*15
        else:
            volume_pdata = pressure_pdata*30

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
        pressPercent = 0
        oxyPercent = 0
        if(fio2_data)>21 and fio2_data > 50:
            oxy_value = float(fio2_data)/100
            if set_ventilator == 1:
                pressPercent = float(volume_pdata)* (1-oxy_value)
                oxyPercent = float(volume_pdata) * oxy_value
            else:    
                pressPercent = float(volume_pdata)
                oxyPercent = float(volume_pdata)
            
        elif(fio2_data)>21 and fio2_data < 51:
            oxy_value = float(fio2_data)/100
            pressPercent = float(volume_pdata) * oxy_value
            oxyPercent = float(volume_pdata) * (1-oxy_value)
        else:
            pressPercent = volume_pdata
            oxyPercent = 0  

        if(mod_val in [2,5]):
            if set_ventilator == 1:
                self.pressureCycleValue = self.readPressureValues(pressPercent,oxyPercent)
            else:
                self.pressureCycleValue = self.readPressureValues(pressPercent,pressPercent)
        if(mod_val in [4,6]):
            if set_ventilator == 1:
                self.pressureCycleValue = self.readPressureValues(pressPercent,oxyPercent)
            else:
                self.pressureCycleValue = self.readvolumeValues(pressure_pdata,pressure_pdata)
        if(mod_val in [3])  :
            if set_ventilator == 1:
                self.pressureCycleValue = self.readPressureValues(pressPercent,oxyPercent)    
            else:
                self.pressureCycleValue = self.readvolumeValues(pressPercent,oxyPercent)

        self.intime = in_time
        self.outtime = out_time
        self.in_t = self.intime 
        self.out_t =  self.outtime 
        

    def stop(self):
        print("stopping breather thread")
        self.pPWM.ChangeDutyCycle(0)
        self.o2PWM.ChangeDutyCycle(0)
        
        GPIO.output(19,GPIO.LOW)
        GPIO.output(14,GPIO.HIGH)
        GPIO.output(26,GPIO.HIGH)

        self.running = False

    def run(self):
        
        global graph,mod_val_data,control,ti_value,ti,two,lamda_b,test
        global ti_val,pressure_support,es,currentP,currentPo
        global mod_val,plan,ex_time,lavs,peep_val,test_ex,fio_val
        global ps_end,check,pressure
        GPIO.output(14,GPIO.LOW)
        self.o2PWM.start(0)
        self.pPWM.start(0)
        QThread.msleep(1)
        

        if (mod_val == 4):
             
             print('in mode4')

             while self.running:
                 end = time.time()+15
                 plan = 0
                 a = 1   
                 while(time.time()<end):

                     if (mod_val_data == 1):

                            graph = 0

                            control = 0
                            ps_pressure_rise = time.time()
                            
                            while(pressure <= pressure_val):
                                self.pwm_ps_in()
      
                            two = time.time()-ps_pressure_rise

                            graph = 1
                            
                            ps_start = time.time()
                            while(pressure >= es):
                                self.pwm_ps_no()
                            ps_end = time.time() - ps_start
                            if(test < es or test < 8):
                                
                                pass

                            mod_val_data =0
                            plan = 1
                            a = 1
                            
                            try:
                                ex_time = lamda_b-lamda
                               
                            except:
                                pass
                     else:
                         graph = 1
                         control = 1
                         if(a == 1):
                             lamda = time.time()
                         
                         self.pwm_ps_out()
                         a = 0
                        
                 if(plan ==0 and mod_val_data == 0):
                      print('mode changed to 1')
                      mod_val = 3
                      check = 1
                      break
        
        if ( mod_val == 3):
            print('mode3')
            while self.running:
                
                self.pwm_in()
                self.pwm_out()
                if (lavs == 1 and mod_val_data == 1 and check == 1):
                    print('inhale start 1')
                    mod_val = 4
                    mod_val_data = 1
                    lavs = 0
                    self.run()
                                  
           
        if mod_val in [2]:
            print('mode 2 enabled')
            while self.running:
                
                self.pwm_in()
                self.pwm_out()


        if (mod_val == 5):
            print('mode 5 enabled')
            while self.running:
                print('mode 5')
                self.pwm_in()
            while(self.running == False):
                    print('mode 5 off')
                    self.pwm_out()
                    time.sleep(2)
                    break
   
    def pwm_in(self):


                global graph,ti,HP_catch
                global control
                control = 0
                HP_catch = 1
                print("self.running.loop")
                print('')
                self.start_time = time.time()
                graph = 0
                
                self.pPWM.ChangeDutyCycle(self.pressureCycleValue[0])
                self.o2PWM.ChangeDutyCycle(self.pressureCycleValue[1])
                print('pressure_cycle:',self.pressureCycleValue[0])
                print('oxygen_cycle:',self.pressureCycleValue[1])
                
                GPIO.output(26,GPIO.LOW)
                GPIO.output(14,GPIO.LOW)

                self.breathStatus = 0
              
                self._inhale_event.wait(timeout=self.in_t)
                self.end = time.time()

                if(mod_val in [1,2,3]):
                    ti = ((self.end) - (self.start_time))
                    ti = round(ti,1)
 
    def pwm_out(self):
                
                global graph,peep_val,ti,currentPo
                global rr_value,test,test_ex,fio_val
                global mod_val_data,mod_val,clear_set
                global control,trigger_value
                print("")

                control = 1
                self.peep = int(peep_val)
                
                graph = 1
                self.p_out_start_time = time.time()
                
                
                self.o2PWM.ChangeDutyCycle(self.peep)
                self.pPWM.ChangeDutyCycle(self.peep)
                
                if(test_ex<= peep_val and currentPo == 1):
                    currentPo = 0

                self.breathStatus = 1
                GPIO.output(14,GPIO.HIGH)
                GPIO.output(26,GPIO.HIGH)
                                
                
                if mod_val in [2,3]:
                    if lavs == 1 and mod_val_data == 1:
                        print("trigger done in modes")
                        self._exhale_event.wait(0)
                        
                        mod_val_data  = 0
                    else:

                         self._exhale_event.wait(timeout=self.out_t)
                self.p_out_end_time = time.time()
                exhale_time = self.p_out_end_time - self.p_out_start_time
                clear_set = 1
                self.end_time = time.time()
           
                try:
           
                    rr_value = int(60/(int(self.end_time) - int(self.start_time)))
                    if fio_val > 85:
                        GPIO.output(19,GPIO.LOW)
                        print("comp_off")
                    else:
                        GPIO.output(19,GPIO.HIGH)
                        print("comp_on")
                except:
                    pass
                    
                    
    def pwm_ps_out(self):
                global graph,peep_val,ti
                global rr_value
                self.peep = int(peep_val)
                graph = 1
                
                self.o2PWM.ChangeDutyCycle(1)
                self.pPWM.ChangeDutyCycle(1)
                GPIO.output(14,GPIO.HIGH)
                GPIO.output(26,GPIO.HIGH)
                self.breathStatus = 1

    
    def pwm_ps_in(self):

                global graph,mod_val_data,ti
                self.start_time = time.time()
                self.pPWM.ChangeDutyCycle(self.pressureCycleValue[0])
                self.o2PWM.ChangeDutyCycle(self.pressureCycleValue[1])
                
                GPIO.output(26,GPIO.LOW)
                GPIO.output(14,GPIO.LOW)
                self.breathStatus = 0
                
                
    def pwm_ps_no(self):
                global graph,peep_val,ti,Slide
                global rr_value
                self.peep = peep_val
                zero = self.pressureCycleValue[0]/2
                one = self.pressureCycleValue[1]/2
#                print('zero',zero)
#                print('one',one)
                graph = 1
                Slide = 1
                self.o2PWM.ChangeDutyCycle(zero)
                self.pPWM.ChangeDutyCycle(one)
                self.breathStatus = 1

    def readPressureValues(self, pressValue, oxValue):
        pressValuFromJson = 0
        oxyValuFromJson = 0
        with open('pressure.json') as data_file:
            data = json.load(data_file)
            for restaurant in data['PressureValues']:
                minSatisfied = int(restaurant['PressureValue']['min'])<=int(pressValue)
                maxSatisfied = int(restaurant['PressureValue']['max'])>=int(pressValue)
                if(minSatisfied and maxSatisfied):
              #      print("pressVal",restaurant['PressureValue']['value'])
                    pressValuFromJson = restaurant['PressureValue']['value']
            for oxyValue in data['OxygenValues']:
                minSatisfied = int(oxyValue['OxygenValue']['min'])<=int(oxValue)
                maxSatisfied = int(oxyValue['OxygenValue']['max'])>=int(oxValue)
                if(minSatisfied and maxSatisfied):
          #         print("Oxygen",oxyValue['OxygenValue']['value'])
                    oxyValuFromJson = oxyValue['OxygenValue']['value']

            return pressValuFromJson,oxyValuFromJson
    def readvolumeValues(self, pressValue, oxValue):
        pressValuFromJson = 0
        oxyValuFromJson = 0
        with open('volume.json') as data_file:
            data = json.load(data_file)
            for restaurant in data['VolumeValues']:
                minSatisfied = int(restaurant['VolumeValue']['min'])<=int(pressValue)
                maxSatisfied = int(restaurant['VolumeValue']['max'])>=int(pressValue)
                if(minSatisfied and maxSatisfied):
#                    print("VolumeValues satisy")#,restaurant['VolumeValue']['value'])
                    pressValuFromJson = restaurant['VolumeValue']['value']
            for oxyValue in data['OxygenValues']:
                minSatisfied = int(oxyValue['OxygenValue']['min'])<=int(oxValue)
                maxSatisfied = int(oxyValue['OxygenValue']['max'])>=int(oxValue)
                if(minSatisfied and maxSatisfied):
          #         print("Oxygen",oxyValue['OxygenValue']['value'])
                    oxyValuFromJson = oxyValue['OxygenValue']['value']

            return pressValuFromJson,oxyValuFromJson        
        

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
        self.seam = []
        self.currentPressure_list = []
        self.average_pressure = []
        #GPIO.setup(4, GPIO.OUT)

    def stop(self):
        global emergency
        emergency = 0
        print("stopping thread")
        self.running = False
        
        
    def initSerData(self):
        
        print('init_ser')
        
       
        
    def sendValues(self):
        #GPIO.output(4,GPIO.HIGH)
        #time.sleep(0.2)
        #GPIO.output(pin,GPIO.LOW)
        data2transfer = self.dataUpdate["pressure"]+','+self.dataUpdate["intime"]+','+self.dataUpdate["outtime"]+','+self.dataUpdate["peep"]+','+self.dataUpdate["fio2"]
        print("DEBUG: "+data2transfer)
        #self.ser1.write(data2transfer.encode())
       

    def getDataAndProcessMode(self):
        global control,lamda_b,lavs,in_time,ex_time
        global adc,ti_val,ti_value,test
        global pressure_support,pressure_val,volume_val
        global trigger_data,Slide
        global graph,mod_val_data,currentP,currentPo
        global value,peep_val,test_ex,pressure
        global emergency
        global fio_val,ps_end,es,mod_val,clear_set
        global pressure_voltage
        
         
         
        ko = 0
         
        slide_p = int(pressure_val+peep_val)
        slide_peep = int(pressure_val)/4



        try:
            if clear_set == 1:
                self.dataDict["Dpress+"].clear()
                
                self.currentPressure_list.clear()
                self.seam.clear()
                clear_set = 0
            if mod_val == 5 and len(self.dataDict["Dpress+"])<30:
                self.dataDict["Dpress+"].clear()
                    
        except:
            drk = 1
        a = True
        ALLOWABLE_PERCENT = 0.1 #10 PERCENT
        #inhale = graph
#        print("GRAPH>>>>",graph)
        ADCdata = [0]*4
        MAX_TRIGGER = -10
        
        for i in range(4):
            try:
                ADCdata[i] = adc.read_adc(i, gain=GAIN)
                time.sleep(0.05)
                if(a==True):
                    oxy_data = ADCdata[2]
                    oxy = int(oxy_data)
                    if oxy == 0:
                        oxy = 112
                    oxy = oxy - oxygen_voltage       #calibrated voltage was minused with the current sensor voltage,if the oxygen sensor gives more voltage 
                    oxy = int(oxy)
                    oxy = oxy*0.1875
                    if oxy > 0:
                        oxy_value = oxy
                    if oxy <= 0:
                        oxy = oxy_value               #conuslt with authority for oxygen value is zerpo
                    self.dataDict["o2conc"].append(oxy)
                    pVolts = (ADCdata[0]/8000)
                    pVolts = round(pVolts,2)
                    pressure = ((pVolts - pressure_voltage)/0.2)*5
                    pressure = round(pressure,1)
                    
                    print('>> pVolts >>', pVolts)
                    print('>> pressure_voltage >>', pressure_voltage)
                    print('>> pressure >>', pressure)
                    if pressure < MAX_TRIGGER:
                        pressure = 0
                    self.average_pressure.append(pressure)
#                    print("average_pressure",self.average_pressure)
                    if graph == 1:
                        self.average_pressure.clear()
                        
                    if len(self.average_pressure)>4 and graph == 0:
                        average = sum(self.average_pressure)/len(self.average_pressure)
                        self.average_pressure.pop(0)
#                        print("after_pop",self.average_pressure)
                        pressure = average
                        
                    dPresLength = len(self.dataDict["Dpress+"])
                    
                                        
                    if(dPresLength == 0):
                        self.dataDict["Dpress+"].append(pressure)
                    if(graph == 0):    
                        if(dPresLength>0):
                            previousPressure = self.dataDict["Dpress+"][dPresLength-1]
                            
                            discountPressure = previousPressure * ALLOWABLE_PERCENT
                            previousPressure = previousPressure - discountPressure
                            if(pressure > previousPressure):
                                self.dataDict["Dpress+"].append(pressure)
                            else:
                                self.dataDict["Dpress+"].append(previousPressure)
                            

                    if(len(self.dataDict["Dpress+"])>300):
 #                       self.dataDict.clear()
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

                    #
                    if mod_val in [3,4,6]:
                       
                        max_value = max(self.dataDict["Dpress+"])

                        if(pressure_val < max_value):
                            emergency = 3
                        if (pressure_val > max_value):
                            emergency = 6
                        if (pressure_val == max_value):
                            emergency = 9      

                if (graph == 1):
                    
                    

                    self.currentPressure_list.append(pressure)
                    Entry_point = len(self.currentPressure_list)
                    p = abs(self.currentPressure_list[-1])
                    disconnect =self.currentPressure_list[10:]
                    print("disconnect",disconnect)
                     
                    if Entry_point >= 10:
                        print("disconnect",disconnect)
                        disconnect_alarm = sum(disconnect)/len(disconnect) 
                        disconnect_alarm = round(disconnect_alarm,1)
                        
                    if mod_val in [2,3] and Entry_point >= 10 and Entry_point < 20:
                        if(disconnect_alarm <= 0):
                            emergency = 1
                        else:
                            emergency = 0
                            
  
                    currentP = pressure
                    test_ex= pressure

                    peep_var = peep_val+2

                        
                    if(mod_val in [2,3,4,6]):
                        
                       
                        self.false_trigger = len(self.currentPressure_list)

                        if (control == 1 and currentP < trigger_data):
                            if self.false_trigger > 10 :# trigger_data):
                                lamda_b = time.time()
                                
                                mod_val_data = 1
                                lavs = 1
                                print('set_pre,act_pre: ',trigger_data,currentP)

                    
                    if(len(self.dataDict["Dpress+"])>300):
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
                    
                    
                    if (Slide == 1):
                        
                        for i in np.arange(slide_p,slide_peep,-0.5):
                            roundi = round(i,1)
                            #template for making ps graph as tangent
         #                   self.dataDict["Dpress+"].append(roundi)
                            Slide = 0
                    
                    test = pressure
                 
                    if test > peep_val:
                        test_final = test
                    else:

                        test_final = test#peep_va      #use template when peep is maintained
           
                    self.seam.append(test_final)
                    if len(self.seam)>4:
                        self.s = self.seam[-1]
                    else:
                        self.s = abs(self.seam[-1])

                  
                    if (self.s < peep_var):
                        currentPo = 1

                    self.dataDict["Dpress+"].append(self.s)

                   
            except:
                pass
               
            
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
           data_m = self.getDataAndProcessMode()
          
        print("stopped thread")
        print('bworker',data_m)
        #self.threadSignal.emit(self.startParm)



class App(QFrame):

    def __init__(self):
        super().__init__()
        self.title = 'ventilator'
        self.pmean = []
        self.mean = []
        self.xaxis = []
        
        self.mean_v = 0
        
        self.left = 10
        self.top = 10
        self.width = 200
        self.height = 100
        self.on = 0
        
        self.initUI()
        self.ie_value = 2
      
        self.setStyleSheet("background-color: black;")
        
        self.bthThread = breathWorker()
        self.bthThread.stopSignal.connect(self.bthThread.stop)
        
        self.beThread = backendWorker('hello')

        self.beThread.stopSignal.connect(self.beThread.stop)
        self.comp_warning()
        self.update_parameters()
        self.graph()
        self.value_set()
       # self.fio2_set()
        self.encoder()
        self.pressureGraph_enable = True
        self.volumeGraph_enable = False

        
    def comp_warning(self):
        global comp_on
        
        if comp_on == False:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText("Connect the compressor and click Ok")
            msgBox.setWindowTitle("No Compressor!!")
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        #msgBox.buttonClicked.connect(msgButtonClick)

            returnValue = msgBox.exec()
            if returnValue == QMessageBox.Ok:
                  print('OK clicked')
        

        
    def fetch_data(self):
        
        ## computing breathing intervals ##
        global in_time,out_time,bpm_val

        bpm = bpm_val
        print('bpm_val',bpm_val)
        ie_pdata = int(self.ie_value)
        
        self.breathCount = 60 / int(bpm)
        print('breathcount',self.breathCount)
    
        self.inhaleTime = (self.breathCount/(ie_pdata+1)) 
        self.exhaleTime = (self.breathCount ) - self.inhaleTime
        
#        print('ie',ie_pdata)        
        in_time = self.inhaleTime
        out_time = self.exhaleTime

    def update_parameters(self):
        self.pressure_value = False 
        self.volume_value = False
        self.bpm_value = False
        self.fio2_value = False
        self.peep_value = False   
        
    def graph(self):

        pg.setConfigOptions(antialias=True)
        self.graphwidget = pg.PlotWidget()
        self.graphwidget.setYRange(0,50)
        #self.graphwidget.setXRange(0,200)
#        self.graphwidget.setXRange(timestamp(), timestamp() + 100)

        self.y = [randint(0,0) for _ in range(200)]  # 100 data points
        self.x = list(range(200))
        
        self.graphwidget.setBackground('#0000')
        self.graphwidget.setLabel('left', 'Pressure')
        self.graphwidget.setLabel('bottom', 'x100 (Time in milliseconds) ')
        #self.graphwidget.getPlotItem().hideAxis('bottom')

        pen = pg.mkPen(color='y')
        self.data_line =  self.graphwidget.plot(self.x, self.y,pen=pen) #fillLevel=0,brush=(150,50,150,50))           #pen=pen)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer_a = QtCore.QTimer()
        self.timer_a.setInterval(1000 )
        self.timer_a.timeout.connect(self.alarm_data)
        self.timer.start()
        self.timer_a.start()
        self.layout.addWidget(self.graphwidget,2,0,5,4)
        #self.data_line.clear()
    def pressureGraph_button(self):
        self.pressureGraph_enable = True
        self.volumeGraph_enable = False
        self.graph()
        self.pressureGraph.setStyleSheet("background-color: black; color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.volumeGraph.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        
    def alarm_data(self):
        global emergency,Hp,Hv,HP_catch
        a = 0
        if emergency != 0:


            if emergency == 1:
                self.alarm.setFont(QFont('Arial', 13))
                self.alarm.setText('Circuit Disconnect') 
                self.alarm.setStyleSheet("color: white;  background-color: red")
#                time.sleep(0.5)
#                self.alarm.setText('disconnect')
            if emergency in [3,6,9]:
                if emergency == 3: 
                    self.lpresd.setText('High-Pr')
                if emergency == 6:
                    self.lpresd.setText('Low-Pr')
              #  self.lpresd.setStyleSheet("color: white;  background-color: red")
                
                if HP_catch == 1:
                    Hp +=1
                    HP_catch = 0    
     #               print("hpp",Hp)
                if Hp >= 5:
                    Hp = 0
                    if emergency == 3: 
                        self.alarm.setText('High-Pr')
                    if emergency == 6:
                        self.alarm.setText('Low-Pr')
                    
#                    self.alarm.setText('High-Pr')
                    self.alarm.setStyleSheet("color: white;  background-color: red")
                    if emergency == 9:
                        self.alarm.setStyleSheet("color: white;  background-color: green")
                    
            if emergency == 2:
                self.lmvd.setText('High-vol')
                Hv +=1
                if Hv > 5:
                    self.alarm.setText('High-vol')
                self.lmvd.setStyleSheet("color: white;  background-color: red")

        else:
            self.alarm.setText('-')
            self.alarm.setStyleSheet("color: white;  background-color: black")            
            self.lpresd.setStyleSheet("color: white;  background-color: green")
            self.lmvd.setStyleSheet("color: white;  background-color: green")
            if HP_catch == 1 and emergency == 0:
                Hp = 0
            
        #emergency = 0
        
    def alarm_stop(self):
        global emergency,Hp,Hv
        Hp = 0
        Hv = 0
    
    def update_plot_data(self):
        
        global data_m,rr_value,ti,mod_val,pressure_val,pressure_pdata,two,ex_time
        global pressure,fio_val,Cordinate
        if self.bthThread.breathStatus == 0:
            global data_m,peep_val
            
#            tata = max(data_m['Dpress+'])

            try:
                if mod_val != 5:
                    self.bstop.setEnabled(False)
            except:
                pass
            self.lbcadata.setText('Inhale')

            if(mod_val in [4,6]):
                try:
                    ti = round(two,1)
                    self.lbtidata.setText(str(ti))
      
                except:
                    pass
            else:
                self.lbtidata.setText(str(ti))

            if (self.on == 1):
            
                vol = self.lvol.text()
                self.volc = str(vol)
               

            self.lbpeepdata.setText('-')
            self.lmvd.setText('-')
            try:
                a = max(data_m['Dpress+'])
                self.pip = int(a)

                if(mod_val ==5):
                    self.lpresd.setText(str(pressure))#self.pip))
                    self.lbpdata.setText(str(pressure))#self.pip))
                    self.lbpmeandata.setText('-')

                if(mod_val in [4,6,2,3]):
          
                    self.lpresd.setText(str(self.pip))
                    if(mod_val == 2 or mod_val == 3):
                        if self.pip > peep_val:
                            self.lbpdata.setText(str(self.pip))
                            self.lbvedata.setText(str(self.vti_data))
                            
                    if mod_val in [4,6]:
                        if(self.pip > peep_val):
                            self.lbpdata.setText(str(self.pip))
                            self.mean = float((self.pip * ti) + (float(self.peep) * ex_time))
                            self.pmean = self.mean/(ti+ex_time)
                            self.pmean = "{:.1f}".format(self.pmean)
                            self.lbpmeandata.setText(str(self.pmean))
                            VTdata = (self.pmean)
                            VTdata = int(VTdata)
                            self.vte_data = VTdata* 21
                            self.vti_data = VTdata * 28
                            self.lmvd.setText("-")       #vte
                            self.lbvedata.setText(str(self.vti_data))
                            time = int(ex_time-ti)
                            try:
                                rr_value = 60 /(time)
                                rr_value = round(rr_value,1)
                                InRRate = int(self.volc)
                                ExRRate = int(rr_value)
                                rr = (InRRate*ExRRate)/1000
                                self.lrrd.setText(str(rr_value))
                                self.lbrrdata.setText(str(rr))
                            except:
                                pass
                    
                                  
            except:
                pass
                
  
        
        if self.bthThread.breathStatus == 1:

                
            self.bstop.setEnabled(True)
            self.bthThread.update_pwm_Data()
            self.lbcadata.setText('Exhale')
          
            
            self.lbtidata.setText('-')
            self.lbpdata.setText('-')
          
            if(self.on == 1):
               pass
            try:

                if (len(data_m['Dpress+']) > 2):
                    self.peep_d = (data_m['Dpress+'][-1])
                    self.peep = int(self.peep_d)# round(self.peep_d,1)
                    self.lpresd.setText(str(self.peep))
                    self.lbpeepdata.setText(str(self.peep))
                self.lrrd.setText(str(rr_value))
                InRRate = int(self.volc)
                ExRRate = int(rr_value)
                rr = (InRRate*ExRRate)/1000
                self.lbrrdata.setText(str(rr))
                self.mean = float((self.pip * self.inhaleTime) + (float(self.peep) * self.exhaleTime))
     
                if(ti != 0):
                    
                    if(mod_val in [4,6]):
                        self.lbpmeandata.setText('-')
                        self.lbpdata.setText('-')
                        
                        
                    else:    
                        ti = float(ti)
                        total = self.inhaleTime + self.exhaleTime
                        self.pmean  = self.mean / total

                        self.pmean = round(self.pmean,1)
                        self.lbpmeandata.setText(str(self.pmean))
                        VTdata = (self.pmean)
                        VTdata = int(VTdata)
                        self.vte_data = VTdata* 21
                        self.vti_data = VTdata * 28
                        self.lmvd.setText(str(self.vte_data))       #vte
                        self.lbvedata.setText("-")
                              
            except:
                pass
        
        
        try:

                o2 = int(data_m["o2conc"][-1])
                Compare_fio = fio_val*0.1
                fio2 = int(fio_val - Compare_fio)
                
                if( fio2 > o2):
                    self.laprd.setStyleSheet("background-color: red")
                    self.laprd.setText(str(o2))
                   
                else:
                    self.laprd.setStyleSheet("background-color: green")
                    self.laprd.setText(str(o2))
                     

        except:
           pass
            
        #
        try:
            if(self.pressureGraph_enable == True):
                self.y = self.y[1:]
                a = randint(0,100)
                y_data = int(data_m['Dpress+'][-1])
                self.y.append(y_data)
                self.x = self.x[1:]
                self.x.append(self.x[-1] + 1)
                len_x = len(self.x)
                len_y = len(self.y)
                if(len_x > len_y):
                    diff_len = len_x - len_y
                    self.x = self.x[diff_len:]
                
     
                self.data_line.setData(self.x,self.y)

        except:
                pass
         
        
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
        self.layout.addWidget(self.graphWidget,2,0,5,4)

    def update_plot_data2(self):
        if(self.volumeGraph_enable == True):
            self.x2 = self.x2[1:]  # Remove the first y element.
            self.x2.append(self.x2[-1] + 1)  # Add a new value 1 higher than the last.

            self.y2 = self.y2[1:]  # Remove the first 
            self.y2.append( randint(0,100))  # Add a new random value.

            self.data_line2.setData(self.x2, self.y2)  # Update the data.
        
    def volumeGraph_button(self):
        self.pressureGraph_enable = False
        self.volumeGraph_enable = True

        self.graph2()
        self.pressureGraph.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.volumeGraph.setStyleSheet("background-color: black; color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")   

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
        self.bes.hide()
        self.BEs.setVisible(False)
        self.Bpressure.setEnabled(False)
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)

        self.setLayout(windowLayout)
        self.mode_set = 2
        
        self.show()
        #self.showFullScreen()
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
             
    def closeEvent(self,event):
        
        replymsg = QMessageBox.question(self,"exit","click yes to off",QMessageBox.Yes|QMessageBox.No)
        
        
    def label_reset(self):
        self.lpressure.setText('0')
        self.lvol.setText('0')
        self.lbpm.setText('1')
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

        self.Bti.setEnabled(False)
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
        self.Bti.setEnabled(False)
        self.lbpm.setEnabled(False)
        
        self.lvol.setText(str(self.settings["volume"]["default"]))
        self.lbpm.setText(str(self.settings["bpm"]["default"]))
        self.lpeep.setText(str(self.settings["peep"]["default"]))
        self.lfio2.setText(str(self.settings["fio2"]["default"]))
        
    def hfonc(self):
        self.label_reset()
        self.readSettings(2)
        self.Bti.setEnabled(False)
        self.lpressure.setText(str(self.settings["pressure"]["default"]))
        self.lvol.setText(str(self.settings["volume"]["default"]))
        self.lbpm.setText(str(self.settings["bpm"]["default"]))
        self.lpeep.setText(str(self.settings["peep"]["default"]))
        self.lfio2.setText(str(self.settings["fio2"]["default"]))
        
    def pc(self):
        self.label_reset()
        self.readSettings(1)
        self.lpresd.setVisible(True)
        self.Bti.setEnabled(False)
        self.Bvol.setEnabled(False)
        self.lvol.setVisible(False)
        self.Bpressure.setEnabled(True)
        self.lpressure.setVisible(True)
        self.lpressure.setText(str(self.settings["pressure"]["default"]))
        self.lvol.setText(str(self.settings["volume"]["default"]))
        self.lbpm.setText(str(self.settings["bpm"]["default"]))
        self.lpeep.setText(str(self.settings["peep"]["default"]))
        self.lfio2.setText(str(self.settings["fio2"]["default"]))
        
    def p_callback(self, i):

        if(self.p_en == True):
            v = self.label.text()
            value = int(v) + int(i)
            self.slider.setValue(value)
            
        if(self.b_en == True):
            
            v = self.label.text()
            value = int(v) + int(i)
            self.slider.setValue(value)
            
        if(self.pe_en == True):
            v = self.label.text()
            value = int(v) + int(i)
            self.slider.setValue(value)
        
        if(self.ti_en == True):
            v = self.label.text()
            value = int(v) + int(i)
            self.slider.setValue(value)
            
        if(self.f_en == True):
            v = self.label.text()
            value = int(v) + int(i)
            self.slider.setValue(value)
         
        if(self.v_en == True):
            v = self.label.text()
            if(i == 1):
                value = int(v) + int(i) + 49
            if(i == -1):
                value = int(v) + int(i) - 49
                
            self.slider.setValue(value)  
        #print('en_v',value)

    def s_callback(self):
        if(self.p_en == True):
            self.update_val.click()
            
        if(self.b_en == True):
            self.update_val.click()
            
        if(self.pe_en == True):
            self.update_val.click()
        
        if(self.ti_en == True):
            self.update_val.click()
            
        if(self.f_en == True):
            self.update_val.click()
         
        if(self.v_en == True):
            self.update_val.click() 

    def encoder(self):
        
        self.p_en = False
        self.b_en = False
        self.pe_en = False
        self.ti_en = False
        self.fi_en = False
        self.v_en = False
        self.f_en = False
        self.en = pyky040.Encoder(CLK=17, DT=18, SW=27)
        self.en.setup(scale_min=-1, scale_max=1, step=2, chg_callback=self.p_callback, sw_callback = self.s_callback)
        #t = p_en.watch
        #self.en_thread = multiprocessing.Process(self.p_thread)
        self.en_thread = threading.Thread(target=self.en.watch)
        self.en_thread.start()
    
        
    def pressure_set(self):
        global mod_val
        v = self.lpressure.text()
        self.label.setText(v)
        self.Bpressure.setStyleSheet("background-color: black; color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bvol.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bbpm.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bfio2.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bti.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bpeep.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        
        self.slider.setRange(0, 50)
            
        #self.slp.setFocusPolicy(Qt.Stronocus)
        #self.slp.setPageStep(1)
        v = self.lpressure.text()
        #self.lpressure.setText(str(v))
        self.slider.setValue(int(v))
        self.slider.setVisible(True)
        self.update_val.setVisible(True)
        self.label.setVisible(True)
       
        self.v_en = False
        self.p_en = True
        self.b_en = False
        self.pe_en = False
        self.ti_en = False
        self.f_en = False

        
    def update_setp(self):
        global pressure_val

       # self.update_parameters()
        try:
            self.lpressure.setText(self.pressure_values)
            pressure_val = int(self.lpressure.text())
#            print('p update',pressure_val)
        except:
            v = self.plabel.text()
            self.lpressure.setText(v)
           
        pressure_val = int(self.lpressure.text())
        #print('p update',pressure_val)
        self.p_en = False
        #self.p_en = pyky040.Encoder(CLK=7, DT=8, SW=6)
        #self.en_thread.join()
        self.slp.setVisible(False)
        #self.slp.deleteLater()
        self.plabel.setVisible(False)
        self.pupdate_val.setVisible(False)
    def pupdateLabel(self, value):      
        self.plabel.setText(str(value))       
        self.pressure_values = self.plabel.text()

    def bpm_set(self):
        
        v = int(self.lbpm.text())
        self.label.setText(str(v))
        self.Bbpm.setStyleSheet("background-color: black; color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bvol.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bpressure.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bfio2.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bti.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bpeep.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        
        self.slider.setRange(1, 20)
        #self.slbpm.setStyleSheet("QSlider{min-width: 100px; max-width: 100px;} QSlider::groove:vertical{border: 1px solid #262626; width: 30px; background: grey; margin: 0 12px;} QSlider::handle:vertical {background: white; border: 2px #55F4A5; width: 40px; height: 50px; line-height: 20px;margin-top: -4px; margin-bottom: -4px; border-radius: 9px;}") 
        v = int(self.lbpm.text())
        self.slider.setValue(v)
        
        self.slider.setVisible(True)
        self.update_val.setVisible(True)
        self.label.setVisible(True)

        self.v_en = False
        self.p_en = False
        self.b_en = True
        self.pe_en = False
        self.ti_en = False
        self.f_en = False
        
    def update_setbpm(self):
        global bpm_val

        try:
            self.lbpm.setText(self.bpm_v)
            bpm_val = int(self.bpmlabel.text())
            print('update bpm',bpm_val)
        except:    
            bpm_val = self.bpmlabel.text()
            self.lbpm.setText(bpm_val)
        
        self.slbpm.setVisible(False)
        self.bpmlabel.setVisible(False)
        self.bupdate_val.setVisible(False)
        self.b_en = False
        #self.update_parameters()
    
    def bpmupdateLabel(self, value):      
        self.bpmlabel.setText(str(value))
        #self.lbpm.setText(str(value))
        self.bpm_v = str(value)     

    def peep_set(self):
        global peep_val

        v = self.lpeep.text()
        self.label.setText(v)
        self.Bpeep.setStyleSheet("background-color: black; color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bvol.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bpressure.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bfio2.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bti.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bbpm.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")

        self.slider.setRange(0, 20)
        #self.slpeep.setStyleSheet("QSlider{min-width: 100px; max-width: 100px;} QSlider::groove:vertical{border: 1px solid #262626; width: 30px; background: grey; margin: 0 12px;} QSlider::handle:vertical {background: white; border: 2px #55F4A5; width: 40px; height: 50px; line-height: 20px;margin-top: -4px; margin-bottom: -4px; border-radius: 9px;}") 
        peep_val = int(self.lpeep.text())
        self.slider.setValue(int(peep_val))
        self.slider.setVisible(True)
        self.update_val.setVisible(True)
        self.label.setVisible(True)
        
        self.v_en = False
        self.p_en = False
        self.b_en = False
        self.pe_en = True
        self.ti_en = False
        self.f_en = False
        
    def update_setpeep(self):
        global peep_val
        try:
            self.lpeep.setText(self.peep_v)
            peep_val = int(self.peeplabel.text())
            print('update peep',peep_val)
        except:
  #         peep_val = int(self.peeplabel.text())
            self.lpeep.setText(peep_val)
            peep_val = int(self.lpeep.text())
        #print('ui_peep',peep_val)
        self.slpeep.setVisible(False)
        self.peeplabel.setVisible(False)
        self.peepupdate_val.setVisible(False)
        self.pe_en = False
        #self.update_parameters()
    
    def peepupdateLabel(self, value):
        
        self.peeplabel.setText(str(value)) 
        self.peep_v = str(value)
        
    def ti_set(self):

        #self.slti = QSlider(Qt.Vertical, self) 
        self.slider.setRange(0, 100)
        self.Bti.setStyleSheet("background-color: black; color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bvol.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bpressure.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bfio2.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bbpm.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bpeep.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")

        v = self.ti.text()
        self.slider.setValue(int(v))
        self.label.setText(str(v))

        self.slider.setVisible(True)
        self.update_val.setVisible(True)
        self.label.setVisible(True)

        self.v_en = False
        self.p_en = False
        self.b_en = False
        self.pe_en = False
        self.ti_en = True
        self.f_en = False
        
    def update_setti(self):
        global ti_val
        try:
            self.ti.setText(self.ti_v)
        except:
            v = self.tilabel.text()
            self.lfio2.setText(v)
        ti_val = self.ti.text()
        self.slti.setVisible(False)
        self.tilabel.setVisible(False)
        self.tiupdate_val.setVisible(False)
        self.ti_en = False
        #self.update_parameters()
    
    def tiupdateLabel(self, value):      
        self.tilabel.setText(str(value))
        #self.lfio2.setText(str(value))
        self.ti_v = str(value)     
        

    def fio2_set(self):
        global fio_val,set_ventilator

        if set_ventilator == 1:
            self.slider.setRange(0, 100)
        else:    
            self.slider.setRange(70, 100)
            
        self.Bfio2.setStyleSheet("background-color: black; color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bvol.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bpressure.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bti.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bbpm.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bpeep.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")

        self.slider.setValue(70)
        self.lfio2.setText(str(70))
        self.slider.setVisible(True)
        self.update_val.setVisible(True)
        self.label.setVisible(True)

        self.v_en = False
        self.p_en = False
        self.b_en = False
        self.pe_en = False
        self.ti_en = False
        self.f_en = True
        
    def update_setfio2(self):
        global fio_val
        try:
            self.lfio2.setText(self.fio2_v)
            fio_val = int(self.lfio2.text())
            print('update fio2',fio_val)
        except:
            v = self.fio2label.text()
            self.lfio2.setText(v)
        fio_val = int(self.lfio2.text())
        self.slfio2.setVisible(False)
        self.fio2label.setVisible(False)
        self.fupdate_val.setVisible(False)
        self.f_en = False
        #self.update_parameters()
    
    def fio2updateLabel(self, value):      
        self.fio2label.setText(str(value))
        #self.lfio2.setText(str(value))
        self.fio2_v = str(value)     
        
    def value_set(self):
        global slider
        
        if(slider == 0):
            self.slider = QSlider(Qt.Vertical, self) 
            self.slider.setRange(0, 100)
           # self.slider.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.slider.setStyleSheet("QSlider{min-width: 100px; max-width: 100px;} QSlider::groove:vertical{border: 1px solid #262626; width: 30px; background: grey; margin: 0 12px;} QSlider::handle:vertical {background: #55F4A5; border: 2px #55F4A5; width: 40px; height: 50px; line-height: 20px;margin-top: -4px; margin-bottom: -4px; border-radius: 9px;}") 
            self.slider.setFocusPolicy(Qt.NoFocus)
            self.slider.setPageStep(5)
            self.slider.valueChanged.connect(self.updateLabel)
            self.slider.setTickPosition(QSlider.TicksBelow)
            self.slider.setTickInterval(5)
            

            self.label = QLabel('0', self)
            self.label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.label.setMinimumWidth(80)
            self.label.setFont(QFont('Times New Roman', 30))
            self.label.setStyleSheet("color: #55F4A5;  background-color: black")

            self.layout.addWidget( self.slider,2,6,4,1,alignment=Qt.AlignRight)
            self.layout.addWidget(self.label,6,6)
            self.slider.setVisible(False)
            self.label.setVisible(False)

            self.update_val = QPushButton('Update')
            self.update_val.setFont(QFont('Arial', 20))
            self.update_val.setStyleSheet("background-color: black; color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
            #self.update_val.setStyleSheet("background-color: red")
            self.layout.addWidget(self.update_val,7,6)
            self.update_val.clicked.connect(self.update_set)
            self.update_val.setVisible(False)
            slider += 1
        
    def updateLabel(self, value):      
        self.label.setText(str(value))
        self.updated_value = str(value)
    
    def update_set(self):
        global pressure_val,volume_val,bpm_val,fio_val,ti_val,peep_val,fio_val
        
        if(self.p_en == True):
            try:
                self.lpressure.setText(self.updated_value)
                pressure_val = int(self.lpressure.text())
                self.p_en = False
                self.slider.setVisible(False)
                self.label.setVisible(False)
                self.update_val.setVisible(False)
                self.Bpressure.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
                #            print('p update',pressure_val)
            except:
                v = self.label.text()
                self.lpressure.setText(v)
                
        if(self.v_en == True):
            try:
                self.lvol.setText(self.updated_value)
                volume_val = int(self.lvol.text())
                self.v_en = False
                self.slider.setVisible(False)
                self.label.setVisible(False)
                self.update_val.setVisible(False)
                self.Bvol.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
                #            print('p update',pressure_val)
            except:
                volume_val = self.label.text()
                self.lvol.setText(volume_val)
        
        if(self.b_en == True):
            try:
                self.lbpm.setText(self.updated_value)
                bpm_val = int(self.lbpm.text())
                self.Bbpm.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
                self.b_en = False
                self.slider.setVisible(False)
                self.label.setVisible(False)
                self.update_val.setVisible(False)
                #            print('p update',pressure_val)
            except:
                bpm_val = self.label.text()
                self.lbpm.setText(bpm_val)
                
        if(self.ti_en == True):
            try:
                self.ti.setText(self.updated_value)
                ti_val = int(self.ti_val.text())
                self.Bti.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
                self.ti_en = False
                self.slider.setVisible(False)
                self.label.setVisible(False)
                self.update_val.setVisible(False)
                #            print('p update',pressure_val)
            except:
                ti_val = self.label.text()
                self.ti.setText(ti_val)
                
        if(self.pe_en == True):
            try:
                self.lpeep.setText(self.updated_value)
                self.Bpeep.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
                peep_val = int(self.lpeep.text())
                self.pe_en = False
                self.slider.setVisible(False)
                self.label.setVisible(False)
                self.update_val.setVisible(False)
                #            print('p update',pressure_val)
            except:
                peep_val = self.label.text()
                self.lbpm.setText(peep_val)
        
        if(self.f_en == True):
            try:
                self.lfio2.setText(self.updated_value)
                self.Bfio2.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
                fio_val = int(self.lfio2.text())
                self.f_en = False
                self.slider.setVisible(False)
                self.label.setVisible(False)
                self.update_val.setVisible(False)
                #            print('p update',pressure_val)
            except:
                fio_val = self.label.text()
                self.lfio2.setText(fio_val)


    
    def volume_set(self):
       
        #self.slv = QSlider(Qt.Vertical, self)
        self.slider.setRange(50, 1500)
        self.Bvol.setStyleSheet("background-color: black; color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bti.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bpressure.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bfio2.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bbpm.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.Bpeep.setStyleSheet("background-color: white; color: black; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")

        #self.slv.setStyleSheet("QSlider{min-width: 100px; max-width: 100px;} QSlider::groove:vertical{border: 1px solid #262626; width: 30px; background: grey; margin: 0 12px;} QSlider::handle:vertical {background: white; border: 2px #55F4A5; width: 40px; height: 50px; line-height: 20px;margin-top: -4px; margin-bottom: -4px; border-radius: 9px;}") 
        #self.slv.setFocusPolicy(Qt.NoFocus)
        v = self.lvol.text()
        self.slider.setValue(int(v))
        
        self.slider.setVisible(True)
        self.update_val.setVisible(True)
        self.label.setVisible(True)
        #self.slv.setPageStep(5)
        self.v_en = True
        self.p_en = False
        self.b_en = False
        self.pe_en = False
        self.ti_en = False
        self.f_en = False
        
        
    def volume_update(self, value):
        self.vlabel.setText(str(value))
        self.vol_v = str(value)
        
    def lvolume_set(self):
        global volume_val
        #print(self.updated_value) #Updated value
        try:
            self.lvol.setText(self.vol_v)
            volume_val = int(self.lvol.text())
            print('update vol',volume_val)
        except:
            v = self.vlabel.text()
            self.lvol.setText(v)
            volume_val = int(self.lvol.text())
    
        self.slv.setVisible(False)
        self.vlabel.setVisible(False)
        self.vupdate_val.setVisible(False)
        self.update_parameters()
        self.v_en = False
    
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

        
    def ie_update(self):

      self.cb = QComboBox()
      self.cb.addItem("IE Values")
      self.cb.addItem("1:1")
      self.cb.addItem("1:2")
      self.cb.addItem("1:3")
      self.cb.addItem("1:4")
      self.cb.setFont(QFont('Arial', 20))
      self.cb.setStyleSheet("color: black;  background-color: white") 
      self.cb.setGeometry(200, 150, 120, 40)  
      self.layout.addWidget(self.cb,7,4)
      self.cb.currentIndexChanged.connect(self.ie_updated)

    def es_update(self):
        self.bes.showPopup()
        
    def es_value(self,value):
        global es,pressure_val
        
        if(value == 1):
            es = (5*pressure_val)/100
        if(value == 2):
            es = (10*pressure_val)/100
        if(value == 3):
            es = (15*pressure_val)/100
        if(value == 4):
            es = (20*pressure_val)/100           
        if(value == 5):
            es = (25*pressure_val)/100
        if(value == 'None'):
            es = 8
        
    
    def ie_updated(self, value):
        #self.cb.deleteLater()
        global ie_value
        self.ie_value = str(value)
        ie_value = int(value)
   #     print('iev',self.ie_value)
        if(value == 1):
            self.lbrdata.setText("1:1")
        if(value == 2):
            self.lbrdata.setText("1:2")
        if(value == 3):
            self.lbrdata.setText("1:3")
        if(value == 4):
            self.lbrdata.setText("1:4")    
        print('ie',value)
                

    def trigger_update(self):

      self.cbtr = QComboBox()
      self.cbtr.addItem("Trigger")
      self.cbtr.addItem("-8")
      self.cbtr.addItem("-7")
      self.cbtr.addItem("-6")
      self.cbtr.addItem("-5")
      self.cbtr.addItem("-4")
      self.cbtr.addItem("-3")
      self.cbtr.addItem("-2")
      self.cbtr.addItem("-1")
      self.cbtr.setFont(QFont('Arial', 20))
      self.cbtr.setStyleSheet("color: black;  background-color: white") 
      self.cbtr.setGeometry(200, 150, 120, 40)  
      self.layout.addWidget(self.cbtr,5,4)
      self.cbtr.currentIndexChanged.connect(self.trigger_updated)

    def trigger_updated(self, value):
        #self.cbtr.deleteLater()
                                        
        global trigger_data
        if value == 1:
            trigger_data = -8
        if value == 2:
            trigger_data = -7
        if value == 3:
            trigger_data = -6
        if value == 4:
            trigger_data = -5
        if value == 5:
            trigger_data = -4
        if value == 6:
            trigger_data = -3
        if value == 7:
            trigger_data = -2
        if value == 8:
            trigger_data = -1    


    def mode_update(self):

      self.md = QComboBox()
      list = ["VC","PC","SPONT+PS","HFONC","BiPAP"]
      self.md.addItems(list)
      self.md.setFont(QFont('Arial', 20))
      self.md.setStyleSheet("color: black;  background-color: white") 
      self.md.setGeometry(200, 150, 120, 40)  
      self.layout.addWidget(self.md,3,4)
      self.md.currentIndexChanged.connect(self.mode_updated)

    def mode_updated(self, value):
        global mod_val,graph
        #self.md.deleteLater()
        self.mode_set = int(value)+2
        print('mod_set',self.mode_set)
        if self.mode_set in [0,1]:
         #   self.lmode.setText('None')
#            self.Bstart.setEnabled(False)
            self.bes.hide()
            self.BEs.setVisible(False)
            self.Bpressure.setEnabled(False)
            self.lpressure.setVisible(False)
            self.Bti.setEnabled(False)
            self.Bvol.setEnabled(False)
            self.lvol.setVisible(False)
            self.Bbpm.setEnabled(False)
            self.lbpm.setVisible(False)
            self.Bpeep.setEnabled(False)
            self.lpeep.setVisible(False)
            self.Bfio2.setEnabled(False)
            self.lfio2.setVisible(False)
            self.Bpressure.setText('Pressure')
            self.fio2_set()
            print('mode_val',mod_val)
        if self.mode_set == 2:
          #  self.lmode.setText('VC')
            
            mod_val = 2
            self.bes.hide()
#            self.Bstart.setEnabled(True)
            self.BEs.setVisible(False)
            self.Bpressure.setEnabled(False)
            self.lpressure.setVisible(False)
            self.Bti.setEnabled(False)
            self.Bvol.setEnabled(True)
            self.lvol.setVisible(True)
            self.Bbpm.setEnabled(True)
            self.lbpm.setVisible(True)
            self.Bpeep.setEnabled(True)
            self.lpeep.setVisible(True)            
            self.Bfio2.setEnabled(True)
            self.lfio2.setVisible(True)
            self.Bpressure.setText('Pressure')
            self.vc()
            self.lpres.setVisible(True)
            self.lpresd.setVisible(True)
            self.fio2_set()
            print('mode_val',mod_val)
        if self.mode_set == 3:
           # self.lmode.setText('PC')
            mod_val = 3
 #           self.Bstart.setEnabled(True)
            self.Bpressure.setText('Ps')
            self.BEs.setVisible(False)
            self.Bti.setEnabled(False)
            self.Bvol.setEnabled(False)
            self.lvol.setVisible(False)
            self.Bbpm.setEnabled(True)
            self.lbpm.setVisible(True)
            self.Bpeep.setEnabled(True)
            self.lpeep.setVisible(True)
            self.Bfio2.setEnabled(True)
            self.lfio2.setVisible(True)
            self.fio2_set()
            print('mode_val',mod_val)
            self.pc()
        if self.mode_set == 4:
            self.ps()
            #self.lmode.setText('SPONT+PS')
            mod_val = 4
#            self.Bstart.setEnabled(True)
#            self.bes.showPopup()
            self.BEs.setVisible(True)
            self.Bpressure.setEnabled(True)
            self.lpressure.setVisible(True)
            self.Bti.setEnabled(False)
            self.Bvol.setEnabled(False)
            self.lvol.setVisible(False)
            self.Bbpm.setEnabled(False)
            self.lbpm.setVisible(False)
            self.Bpeep.setEnabled(True)
            self.lpeep.setVisible(True)
            self.Bfio2.setEnabled(True)
            self.lfio2.setVisible(True)
            self.Bpressure.setText('PS')
            self.lmvd.setText('-')
            self.lbvedata.setText('-')
            self.fio2_set()
            print('mode_val',mod_val)
        if self.mode_set == 5:
            self.hfonc()
            #self.lmode.setText('HFONC')
            mod_val = 5
#            self.Bstart.setEnabled(True)
            self.bes.hide()
            self.BEs.setVisible(False)
            self.Bpressure.setVisible(True)
            self.lpressure.setVisible(True)
            self.Bpressure.setEnabled(True)
            self.Bpressure.setText('Flow')

            self.Bti.setEnabled(False)
            self.Bvol.setEnabled(False)
            self.lvol.setVisible(False)
            self.Bbpm.setEnabled(False)
            self.lbpm.setVisible(False)
            self.Bpeep.setEnabled(False)
            self.lpeep.setVisible(False)
            self.Bfio2.setEnabled(True)
            self.lfio2.setVisible(True)
            self.fio2_set()
            print('mode_val',mod_val)
            
        if self.mode_set == 6:
            #self.lmode.setText('BiPAP')
            mod_val = 4
#            self.Bstart.setEnabled(True)
#            self.bes.showPopup()
            self.Bpressure.setEnabled(True)
            self.BEs.setVisible(True)
            self.lpressure.setVisible(True)
            self.Bti.setEnabled(False)
            self.Bvol.setEnabled(False)
            self.lvol.setVisible(False)
            self.Bbpm.setEnabled(True)
            self.lbpm.setVisible(True)
            self.Bpeep.setEnabled(True)
            self.lpeep.setVisible(True)
            self.Bfio2.setEnabled(True)
            self.lfio2.setVisible(True)
            self.Bpressure.setText('PS')
            self.lmvd.setText('-')
            self.lbvedata.setText('-')
            self.Bpressure.setText('PS')
            self.fio2_set()
            print('mode_val',mod_val)
    def on_process(self):
        self.alarm.setVisible(True)
        self.fetch_data()
        self.bthThread.update_pwm_Data()
        self.md.setEnabled(False)
        
        self.beThread.running = True
        self.bthThread.running = True
  #      self.disableUI()
        self.beThread.start()
        self.bthThread.start()
        self.on = 1
        self.timer.start()
        self.timer_a.start()

        
    def off_process(self):
        global emergency
  #      print("pressed stop button")
        self.item = 'VC'
        self.md.setCurrentText(self.item)
        self.md.setEnabled(True)
        self.alarm.setVisible(False)
        self.alarm.setText('-')
        self.alarm.setStyleSheet("color: white;  background-color: black")
        emergency = 0
#        self.lbvedata.setText('0')
#        self.lbvedata.setText('0')
     #   print('done')
        self.on = 0
        self.timer.stop()
        self.timer_a.stop()
        self.beThread.stopSignal.emit()
        self.bthThread.stopSignal.emit()
        
#        GPIO.output(14,GPIO.HIGH)
#        GPIO.output(26,GPIO.LOW)
        
        
    def createGridLayout(self):
        global lpressure
        global pressure_val,volume_val,fio_val,peep_val,bpm_val
        self.horizontalGroupBox = QGroupBox() 
        self.layout = QGridLayout()
        self.layout.setColumnStretch(6, 9)
        self.layout.setColumnStretch(6, 9)     

        #Adding push buttons
        self.Bpressure = QPushButton('Pressure') #pressurepush button
        self.Bpressure.setGeometry(0, 0, 100, 40)
        self.Bpressure.setFont(QFont('Arial', 20))  
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
        self.lpressure.setFont(QFont('Arial', 25))
        self.lpressure.setStyleSheet("color: white;  background-color: black")
 #       
        a = str(self.settings["pressure"]["default"])
        self.lpressure.setText(a)
        pressure_val = int(self.lpressure.text())
        self.layout.addWidget(self.lpressure,9,0)
        
        self.Bvol = QPushButton('Volume') #volumePushButton
        self.Bvol.setGeometry(0, 0, 100, 40)
        self.Bvol.setFont(QFont('Arial', 20))
        self.Bvol.setStyleSheet("background-color: white")
        self.Bvol.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.layout.addWidget(self.Bvol,8,1)
        #Bvol.clicked.connect(self.volume_update)
        self.Bvol.clicked.connect(self.volume_set)
        self.Bvol = QPushButton('Volume') #volumePushButton
        self.Bvol.setGeometry(0, 0, 100, 40)
        self.Bvol.setFont(QFont('Arial', 20))
        self.Bvol.setStyleSheet("background-color: white")
        self.Bvol.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.layout.addWidget(self.Bvol,8,1)
        #Bvol.clicked.connect(self.volume_update)
        self.Bvol.clicked.connect(self.volume_set)        
 

        self.BEs = QPushButton('Es %') #GraphRefreshbutton
        self.BEs.setGeometry(0, 0, 100, 40)
        self.BEs.setFont(QFont('Arial', 15))  
        self.BEs.setStyleSheet("background-color: white")
        self.BEs.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.layout.addWidget(self.BEs,8,1)
        self.BEs.clicked.connect(self.es_update)
        self.BEs.clicked.connect(self.es_value)
 
 
        self.lvol = QLabel("0")  #volume label
        self.lvol.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lvol.setFont(QFont('Arial', 25))
        self.lvol.setStyleSheet("color: white;  background-color: black")
        a = str(self.settings["volume"]["default"])
        self.lvol.setText(a)
        volume_val = int(self.lvol.text())
        print('volume_set',volume_val)
        self.layout.addWidget(self.lvol,9,1)
  
        self.Bbpm = QPushButton('BPM')  #BPM PushButton
        self.Bbpm.setGeometry(0, 0, 100, 40)
        self.Bbpm.setFont(QFont('Arial', 20))
        self.Bbpm.setStyleSheet("background-color: white")
        self.Bbpm.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.layout.addWidget(self.Bbpm,8,2)
        self.Bbpm.clicked.connect(self.bpm_set)
        self.Bbpm.clicked.connect(self.bpm_update)

        self.lbpm = QLabel("0")  #BPM label
        self.lbpm.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lbpm.setFont(QFont('Arial', 25))
        self.lbpm.setStyleSheet("color: white;  background-color: black")
        a = str(self.settings["bpm"]["default"])
        self.lbpm.setText(a)
        bpm_val = int(self.lbpm.text())
        self.layout.addWidget(self.lbpm,9,2)

        self.Bpeep = QPushButton('PEEP')  #peep_button
        self.Bpeep.setGeometry(0, 0, 100, 40)
        self.Bpeep.setFont(QFont('Arial', 20))  
        self.Bpeep.setStyleSheet("background-color: white")
        self.Bpeep.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.layout.addWidget(self.Bpeep,8,3)
        self.Bpeep.clicked.connect(self.peep_set)
        self.Bpeep.clicked.connect(self.peep_update)

        self.lpeep = QLabel("0")  #peep label
        self.lpeep.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lpeep.setFont(QFont('Arial', 25))
        self.lpeep.setStyleSheet("color: white;  background-color: black")
        a = str(self.settings["peep"]["default"])
        self.lpeep.setText(a)
        peep_val = int(self.lpeep.text())
        self.layout.addWidget(self.lpeep,9,3)

        self.Bfio2 = QPushButton('fio2')  #fio2 Button
        self.Bfio2.setGeometry(0, 0, 100, 40)
        self.Bfio2.setFont(QFont('Arial', 20))
        self.Bfio2.setStyleSheet("background-color: white")
        self.Bfio2.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.layout.addWidget(self.Bfio2,8,4)
        self.Bfio2.clicked.connect(self.fio2_set)
        self.Bfio2.clicked.connect(self.fio2_update)
#        Bfio2.clicked.connect(self.graph)

        self.lfio2 = QLabel("0")  #fio2 label
        self.lfio2.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lfio2.setFont(QFont('Arial', 25))
        self.lfio2.setStyleSheet("color: white;  background-color: black")
        a = str(self.settings["fio2"]["default"])
        self.lfio2.setText(a)
        fio_val = int(self.lfio2.text())
        self.layout.addWidget(self.lfio2,9,4)
        
        self.Bti = QPushButton('Ti')  #ti Button
        self.Bti.setGeometry(0, 0, 100, 40)
        self.Bti.setFont(QFont('Arial', 20))
        self.Bti.setStyleSheet("background-color: white")
        self.Bti.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        self.layout.addWidget(self.Bti,8,5)
        self.Bti.clicked.connect(self.ti_set)
        self.Bti.setEnabled(False)
        #Bti.clicked.connect(self.ti_update)

        self.ti = QLabel("0")  #ti label
        self.ti.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.ti.setFont(QFont('Arial', 25))
        self.ti.setStyleSheet("color: white;  background-color: black")
        #a = str(self.settings["fio2"]["default"])
        #self.lfio2.setText(a)
        #io_val = int(self.lfio2.text())
        self.layout.addWidget(self.ti,9,5)

        Bmode = QPushButton('Mode') #mode button
        Bmode.setGeometry(0, 0, 100, 400)
        Bmode.setFont(QFont('Arial', 20))
        Bmode.setStyleSheet("background-color: white")
        #self.layout.addWidget(Bmode,3,4)
        self.mode_update()
        #Bmode.clicked.connect(self.mode_update)

        Btrigger = QPushButton('Trigger')  #trigger button
        Btrigger.setGeometry(0, 0, 100, 40)
        Btrigger.setFont(QFont('Arial', 20))
        Btrigger.setStyleSheet("background-color: white")
        self.trigger_update()
        #self.layout.addWidget(Btrigger,4,4)
        #Btrigger.clicked.connect(self.trigger_update)

        self.ltrigger = QLabel("Trigger")  #trigger label
        self.ltrigger.setFont(QFont('Arial', 25))
        self.ltrigger.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(self.ltrigger,4,4)

        self.BIE = QPushButton('I:E')    #IE button
        self.BIE.setGeometry(0, 0, 100, 40)
        self.BIE.setFont(QFont('Arial', 20))
        self.BIE.setStyleSheet("background-color: white")
        self.ie_update()
        #self.layout.addWidget(self.BIE,6,4)
        #self.BIE.clicked.connect(self.ie_update)

        self.lie = QLabel("IE")  #IE label
        self.lie.setFont(QFont('Arial', 25))
        self.lie.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(self.lie,6,4)

        self.lmode = QLabel("Modes")  #mode label
        self.lmode.setFont(QFont('Arial', 25))
        self.lmode.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(self.lmode,2,4)

        ratio = '1:2'                  #breath ratio label
        lbr = QLabel('Breath Ratio')
        lbr.setFont(QFont('Arial', 20))
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
        lbP.setFont(QFont('Arial', 20))
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
        lbpmean.setFont(QFont('Arial', 20))
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
        lbti.setFont(QFont('Arial', 20))
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
        lbca.setFont(QFont('Arial', 20))
        self.lbcadata = QLabel(ca)
        self.lbcadata.setFont(QFont('Arial', 25))
        lbca.setStyleSheet("color: #55F4A5;  background-color: black")
        self.lbcadata.setStyleSheet("color: #55F4A5;  background-color: black")
        lbca.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lbcadata.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        #self.layout.addWidget(lbca,2,6)
        #self.layout.addWidget(self.lbcadata,3,6)

        Ve = '0'                           #Ve label
        lbve = QLabel('VTi')
        lbve.setFont(QFont('Arial', 20))
        self.lbvedata = QLabel(Ve)
        self.lbvedata.setFont(QFont('Arial', 25))
        lbve.setStyleSheet("color: white;  background-color: black")
        self.lbvedata.setStyleSheet("color: white;  background-color: black")
        lbve.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lbvedata.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(lbve,4,6)
        self.layout.addWidget(self.lbvedata,5,6)

        rr = '0'                            #mV label
        lbrr = QLabel('mV')
        lbrr.setFont(QFont('Arial', 20))
        self.lbrrdata = QLabel(rr)
        self.lbrrdata.setFont(QFont('Arial', 25))
        lbrr.setStyleSheet("color: #55F4A5;  background-color: black")
        self.lbrrdata.setStyleSheet("color: #55F4A5;  background-color: black")
        lbrr.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lbrrdata.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(lbrr,6,6)
        self.layout.addWidget(self.lbrrdata,7,6)

        peep = '0'                            #PEEP label
        lbpeep = QLabel('PEEP')
        lbpeep.setFont(QFont('Arial', 20))
        self.lbpeepdata = QLabel(peep)
        self.lbpeepdata.setFont(QFont('Arial', 25))
        lbpeep.setStyleSheet("color: white;  background-color: black")
        self.lbpeepdata.setStyleSheet("color: white;  background-color: black")
        lbpeep.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lbpeepdata.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(lbpeep,8,6)
        self.layout.addWidget(self.lbpeepdata,9,6)
      
        self.Bstart = QPushButton('Start')          #start button
        self.Bstart.setFont(QFont('Arial', 20))
        self.Bstart.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")

        self.Bstart.clicked.connect(self.on_process)
        self.layout.addWidget(self. Bstart,1,6)
        self.Bstart.clicked.connect(self.stop)
        
        self.lalarm = QPushButton('Alarm')
        self.lalarm.setFont(QFont('Arial', 20))
        self.lalarm.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        #self.lalarm.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lalarm.clicked.connect(self.alarm_stop)
        self.layout.addWidget(self.lalarm,0,0)
        self.alarm = QLabel('-')
        self.alarm.setFont(QFont('Arial', 20))
        self.alarm.setStyleSheet("color: white;  background-color: black")
        self.layout.addWidget(self.alarm,1,0)
        
         
        self.lgas = QLabel('Air-Pr')
        self.lgas.setFont(QFont('Arial', 20))
        self.lgas.setStyleSheet("color: white;  background-color: black")
        self.lgas.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lgas,0,1)

        self.lgasd = QLabel('Normal')
        self.lgasd.setFont(QFont('Arial', 25))
        self.lgasd.setStyleSheet("color: white;  background-color: green")
        self.lgasd.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lgasd,1,1)

        self.lapr = QLabel('O2 %')
        self.lapr.setFont(QFont('Arial', 20))
        self.lapr.setStyleSheet("color: white;  background-color: black")
        self.lapr.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lapr,0,2)

        self.laprd = QLabel('0')
        self.laprd.setFont(QFont('Arial', 25))
        self.laprd.setStyleSheet("color: white;  background-color: green")
        self.laprd.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.laprd,1,2)

        self.lpres = QLabel('Pressure')
        self.lpres.setFont(QFont('Arial', 25))
        self.lpres.setStyleSheet("color: white;  background-color: black")
        self.lpres.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lpres,0,4)

        self.lpresd = QLabel('0')
        self.lpresd.setFont(QFont('Arial', 25))
        self.lpresd.setStyleSheet("color: white;  background-color: green")
        self.lpresd.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lpresd,1,4)

        self.lmv = QLabel('VTe')
        self.lmv.setFont(QFont('Arial', 20))
        self.lmv.setStyleSheet("color: white;  background-color: black")
        self.lmv.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lmv,0,3)

        self.lmvd = QLabel('0')
        self.lmvd.setFont(QFont('Arial', 25))
        self.lmvd.setStyleSheet("color: white;  background-color: green")
        self.lmvd.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lmvd,1,3)


        self.lrr = QLabel('RR')
        self.lrr.setFont(QFont('Arial', 20))
        self.lrr.setStyleSheet("color: white;  background-color: black")
        self.lrr.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lrr,0,5) 

        self.lrrd = QLabel('0')
        self.lrrd.setFont(QFont('Arial', 25))
        self.lrrd.setStyleSheet("color: white;  background-color: green")
        self.lrrd.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lrrd,1,5) 

        self.llogo = QLabel('Bravo...')
        self.llogo.setFont(QFont('Gabriola', 25))
        self.llogo.setStyleSheet("color: maroon;  background-color: black")
        self.llogo.setAlignment(Qt.AlignLeft | Qt.AlignLeft)
     
        self.lpower = QLabel('MAIN POWER')
        self.lpower.setFont(QFont('Arail', 18))
        self.lpower.setStyleSheet("color: white;  background-color: green")
        self.lpower.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.lpower,0,6)
        
        self.pressureGraph = QPushButton('Pressure Graph')
        self.pressureGraph.setFont(QFont('Arial', 11))
        self.pressureGraph.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        #self.lalarm.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.pressureGraph.clicked.connect(self.pressureGraph_button)
        self.layout.addWidget(self.pressureGraph,7,1)
        
        self.volumeGraph = QPushButton('Volume Graph')
        self.volumeGraph.setFont(QFont('Arial', 11))
        self.volumeGraph.setStyleSheet("background-color: white; border-style: outset; border-width: 2px; border-radius: 15px; border-color: #55F4A5; padding: 4px;")
        #self.lalarm.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.volumeGraph.clicked.connect(self.volumeGraph_button)
        self.layout.addWidget(self.volumeGraph,7,2)

        self.bes = QComboBox()
        self.bes.addItem("ES %")
        self.bes.addItem("5")
        self.bes.addItem("10")
        self.bes.addItem("15")
        self.bes.addItem("20")
        self.bes.addItem("25")
        self.bes.setFont(QFont('Arial', 20))
        self.bes.setStyleSheet("color: black;  background-color: white")
        self.bes.setGeometry(200, 150, 120, 40)  
        self.layout.addWidget(self.bes,9,1)
        self.bes.currentIndexChanged.connect(self.es_value)
        
        self.horizontalGroupBox.setLayout(self.layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
