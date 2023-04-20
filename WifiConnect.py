# Author: QuangHa
# Doc: https://docs.micropython.org/en/latest/library/network.WLAN.html

import network
from picozero import pico_led
from time import sleep

class WIFI:
    def __init__(self, ssid=None, password=None, mode=0):
        # enable station interface and connect to WiFi access point# enable station interface and connect to WiFi access point
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.connect(ssid, password)
        wait = 50
        wlanStatus = None
        while self.wlan.isconnected() == False and wait >= 0:
            if wait % 2 == 0:
                pico_led.on()
            else:
                pico_led.off()
            wlanStatus = self.wlan.status()
            print("Waiting for connection...{}".format(wait))
            if wlanStatus < 0 or wlanStatus >= 3:
                print("wifi connection failed!")
                break
            wait -= 1
            sleep(0.25)
        # Handle connection error
        if self.wlan.isconnected() == False:
            print("wifi connection failed!")
            pico_led.off()
        else:
            pico_led.on()
            print("Connected: {}".format(ssid))
            print("IP.......: {}".format(self.wlan.ifconfig()[0]))
            print("Subnet...: {}".format(self.wlan.ifconfig()[1])) 
            print("Gateway..: {}".format(self.wlan.ifconfig()[2]))

    @property
    def Status(self):
        #STAT_IDLE – no connection and no activity,
        #STAT_CONNECTING – connecting in progress,
        #STAT_WRONG_PASSWORD – failed due to incorrect password,
        #STAT_NO_AP_FOUND – failed because no access point replied,
        #STAT_CONNECT_FAIL – failed due to other problems,
        #STAT_GOT_IP – connection successful.
        return self.wlan.status()

    @property
    def IpAddress(self):
        if self.wlan.isconnected():
            return self.wlan.ifconfig()[0]
        return None
    
    @property
    def Subnet(self):
        if self.wlan.isconnected():
            return self.wlan.ifconfig()[1]
        return None  
      
    @property
    def Gateway(self):
        if self.wlan.isconnected():
            return self.wlan.ifconfig()[2]
        return None
    
    @property
    def isConnected(self):
        return self.wlan.isconnected()
    
    def Disconnect(self):
        self.wlan.disconnect()