from machine import Pin, SPI, I2C
import st7789
from time import sleep
import secrets
import network
from picozero import pico_temp_sensor, pico_led
import ntptime
import time
from ds3231_port import DS3231
import utime

BACKLIGHT_PIN = 10
RESET_PIN = 11
DC_PIN = 12
CS_PIN = 13
CLK_PIN = 14
DIN_PIN = 15 # lower left corner
i2c = I2C(id=0,sda=Pin(4), scl=Pin(5))
ds3231 = DS3231(i2c)

import vga2_8x16 as font

def connect(tft):
    #Connect to WLAN
    ip = ''
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.ssid, secrets.password)
    wait = 50
    wlanstatus = None
    wlanNewStatus = None
    while wlan.isconnected() == False and wait >= 0:
        if wait % 2 == 0:
            pico_led.on()
        else:
            pico_led.off()
        wlanNewStatus = wlan.status()
        #if wlanstatus != wlanNewStatus:
        wlanstatus = wlanNewStatus
        Render(tft, "Waiting for connection...{}".format(wait), 10, 18)
        if wlanNewStatus < 0 or wlanNewStatus >= 3:
            Render(tft, "wifi connection failed!", 10, 36)
            break
        wait -= 1
        sleep(0.2)
    # Handle connection error
    if wlan.isconnected() == False:
        Render(tft, "wifi connection failed!", 10, 36)
        pico_led.off()
    else:
        pico_led.on()
        Render(tft, "Connected: {}".format(secrets.ssid), 10, 36)
        Render(tft, "IP.......: {}".format(wlan.ifconfig()[0]), 10, 54)
        Render(tft, "Mac......: {}".format(wlan.ifconfig()[1]), 10, 72) 
        Render(tft, "Gateway..: {}".format(wlan.ifconfig()[2]), 10, 90)
        ip = wlan.ifconfig()[0]
    return ip
    
def InitDisplay():
    spi = SPI(1, baudrate=31250000, sck=Pin(CLK_PIN), mosi=Pin(DIN_PIN))
    tft = st7789.ST7789(spi, 240, 320,
        reset=Pin(RESET_PIN, Pin.OUT),
        cs=Pin(CS_PIN, Pin.OUT),
        dc=Pin(DC_PIN, Pin.OUT),
        backlight=Pin(BACKLIGHT_PIN, Pin.OUT),
        rotation=4)
    tft.init()
    Render(tft, "TFT display is initialized", 10, 0)
    return tft
    
def Render(tft, text, screen_x, screen_y):
    tft.text(font, text, screen_x, screen_y, st7789.color565(255,255,255), st7789.color565(0,0,0))

def GetTime(tft,ip):
    if ip != '':
        ntptime.host = "1.europe.pool.ntp.org"
        ntptime.settime()
        ds3231.save_time()
    count = 0
    currentTime = None
    while True:
        if ip != '':
            currentTime = utime.localtime()
        else:
            currentTime = ds3231.get_time()
        timestring = "{}/{}/{} {}:{}:{}".format(str(currentTime[0]), str(currentTime[1]), str(currentTime[2]), str(currentTime[3]), str(currentTime[4]), str(currentTime[5]))
        Render(tft, timestring, 10, 126)
        count += 1
        sleep(0.1)
        #if count > 200:
        #    return
        
def Start():
    tft = InitDisplay()
    ip = connect(tft)
    GetTime(tft,ip)
