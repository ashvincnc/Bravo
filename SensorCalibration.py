import Adafruit_ADS1x15

class Calibration:
    def __init__(self):
        self.adc = Adafruit_ADS1x15.ADS1115(address=0x48)
        
    def pressure_calibration(self):
        volt_list = []
        for i in range(20):
            self.data = self.adc.read_adc(0, gain=1)
            volt = self.data/8000
            volt = round(volt,2)
            volt_list.append(volt)
            voltage = sum(volt_list)/len(volt_list)
            voltage = round(voltage,2)
            #print('adc_val',voltage)      
        return voltage
    def oxygenSensor_alert(self):
        volt_list = []
        for i in range(200):
            self.data = self.adc.read_adc(2, gain=1)
            volt = self.data
            volt = round(volt,1)
            volt_list.append(volt)
            voltage = sum(volt_list)/len(volt_list)
            voltage = round(voltage,1)
            
        return voltage
        
    def oxygen_calibration(self):
        volt_list = []
        for i in range(200):
            self.data = self.adc.read_adc(2, gain=1)
            volt = self.data
            volt = round(volt,1)
            volt_list.append(volt)
            voltage = sum(volt_list)/len(volt_list)
            voltage = round(voltage,1)
            #print( '>>> Voltage >>>>', voltage)
            volt_factor = 21/voltage

        return volt_factor
    
