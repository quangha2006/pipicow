from machine import Pin, SPI, I2C, RTC, ADC
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

analogIn0 = ADC(Pin(26, mode=Pin.IN))
analogIn4 = ADC(4)

ds3231 = DS3231(i2c)

import vga2_8x16 as font
import vga2_16x32 as font_L
import vga2_bold_16x32 as font_L_B
import vga2_16x16 as font_M

def connectWifi(tft):
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
    Render(tft, "Initializing....", 10, 0)
    return tft

def WeekFromInt(dayinweek):
    if dayinweek == 0:
        return "Mon"
    elif dayinweek == 1:
        return "Tue"
    elif dayinweek == 2:
        return "Web"
    elif dayinweek == 3:
        return "Thu"
    elif dayinweek == 4:
        return "Fri"
    elif dayinweek == 5:
        return "Sat"
    elif dayinweek == 6:
        return "Sun"
    return ""
        
def MonthFromInt(monthinyear):
    if monthinyear == 1:
        return "Jan"
    elif monthinyear == 2:
        return "Feb"
    elif monthinyear == 3:
        return "Mar"
    elif monthinyear == 4:
        return "Apr"
    elif monthinyear == 5:
        return "May"
    elif monthinyear == 6:
        return "Jun"
    elif monthinyear == 7:
        return "Jul"
    elif monthinyear == 8:
        return "Aug"
    elif monthinyear == 9:
        return "Sep"
    elif monthinyear == 10:
        return "Oct"
    elif monthinyear == 11:
        return "Nov"
    elif monthinyear == 12:
        return "Dec"
    return ""
        
def Render(tft, text, screen_x, screen_y, font_size = font, color = [255,255,255], bg = [0,0,0]):
    tft.text(font_size, text, screen_x, screen_y, st7789.color565(color[0],color[1],color[2]), st7789.color565(bg[0],bg[1],bg[2]))

def GetTime(tft, ip, run_button):
    tft.fill(st7789.BLACK)
    if ip != '':
        ntptime.host = "1.europe.pool.ntp.org"
        ntptime.settime()
        ds3231.save_time()
    else:
        ds3231.get_time(True)
    currentTime = None
    while True:
        #Render(tft, "            ", 0, 0, font_L_B, [134,156,152], [134,156,152])
        tft.fill_rect(0,0,240,32,st7789.color565(134,156,152))
        Render(tft, "QUANG HA", 60, 0, font_L_B, [255,255,255], [134,156,152])
        currentTime = utime.localtime()
        #format: web, 25 May, 2023
        date_string = "{},{} {},{}".format(WeekFromInt(currentTime[6]),currentTime[2], MonthFromInt(currentTime[1]), currentTime[0])
        time_string = "{:02}:{:02}:{:02}".format(currentTime[3], currentTime[4], currentTime[5])
        year_string = "{}".format(currentTime[0])
        Render(tft, time_string, 60, 38, font_L_B, [81,207,102])
        Render(tft, date_string, 0, 78, font_M)
        #Render(tft, year_string, 120, 138, font_M)
        temp0 = "Temp0: {}".format(ds3231.get_temperature())
        Render(tft, temp0, 10, 144)
        ADC_voltage = analogIn4.read_u16() * (3.3 / (65535))
        temperature_celcius = 27 - (ADC_voltage - 0.706)/0.001721
        temp1 = "Temp1: {:.2f}".format(temperature_celcius)
        Render(tft, temp1, 10, 162)
        sensorValue = analogIn0.read_u16()
        voltage = sensorValue * (3.3 / 65535) * 5.0
        volString = "Voltage: {:.2f}".format(voltage)
        Render(tft, volString, 10, 180)
        sleep(1.0)
        if run_button.value() == 1:
            return
        
def Start(run_button):
    tft = InitDisplay()
    ip = connectWifi(tft)
    GetTime(tft, ip, run_button)
