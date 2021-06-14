import board
import busio
i2c = busio.I2C(board.SCL, board.SDA)
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


class oxygen_alert:
    def __init__(self):
        ads = ADS.ADS1115(i2c)
        ads.gain = 8
        oxy = []
        for i in range(20):
            chan_o = AnalogIn(ads, ADS.P2)
            volt = chan_o.voltage*1000
            volt = int(volt)
            oxy.append(volt)
        self.oxy_volt = sum(oxy)/len(oxy)
     
    def oxygen_voltage(self):
        voltage = self.oxy_volt
        #voltage = 1
        return voltage

