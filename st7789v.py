# document: https://www.coderdojotc.org/micropython/displays/graph/14-lcd-st7789V/#uploading-the-st7789v-python-firmware
# https://github.com/russhughes/st7789_mpy
from machine import Pin, SPI, I2C, RTC, ADC
import st7789
from time import sleep
import secrets
import network
from picozero import pico_temp_sensor, pico_led
from PiicoDev_ENS160 import PiicoDev_ENS160
import ntptime
import time
from ds3231_port import DS3231
import utime
import machine
import aht
from bmp280 import BMP280
import bmp280

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

common_scl=Pin(5)
common_sda=Pin(4)
common_freq=400000
common_id=0
common_i2c=I2C(id=common_id,scl=common_scl, sda=common_sda, freq=common_freq)
        
def Render(tft, text, screen_x, screen_y, font_size = font, color = [255,255,255], bg = [0,0,0]):
    tft.text(font_size, text, screen_x, screen_y, st7789.color565(color[0],color[1],color[2]), st7789.color565(bg[0],bg[1],bg[2]))
    
def RenderRec(tft, x, y, width, height, color = [255,255,255]):
    tft.fill_rect(x, y, width, height, st7789.color565(color[0],color[1],color[2]))
    


def InitSensor():
    sensor = PiicoDev_ENS160(bus=common_id, scl=common_scl, sda=common_sda, freq=common_freq)
    return sensor

def InitBMP280():
    bmp = BMP280(common_i2c)
    bmp.use_case(bmp280.BMP280_CASE_INDOOR)
    return bmp
    
def RenderScreen(tft, run_button,ens160,aht_sensor,bmp_sensor):
    tft.fill(st7789.BLACK)
    #Screen not change
    RenderRec(tft,0,0,240,32,[134,156,152])
    Render(tft, "QUANG HA", 60, 0, font_L_B, [255,255,255], [134,156,152])
    while True:
        beginy=100
        space=18
        currentTime = utime.localtime()
        #format: web, 25 May, 2023
        date_string = "{},{} {},{}".format(WeekFromInt(currentTime[6]),currentTime[2], MonthFromInt(currentTime[1]), currentTime[0])
        time_string = "{:02}:{:02}:{:02}".format(currentTime[3], currentTime[4], currentTime[5])
        year_string = "{}".format(currentTime[0])
        Render(tft, time_string, 60, 38, font_L_B, [81,207,102])
        Render(tft, date_string, 0, 78, font_M)
        #Render(tft, year_string, 120, 138, font_M)
        temp0 = "Temp0: {}".format(ds3231.get_temperature())
        
        ADC_voltage = analogIn4.read_u16() * (3.3 / (65535))
        temperature_celcius = 27 - (ADC_voltage - 0.706)/0.001721
        temp1 = "Temp1: {:.2f}".format(temperature_celcius)
        
        sensorValue = analogIn0.read_u16()
        voltage = sensorValue * (3.3 / 65535) * 5.0
        volString = "Voltage: {:.2f}".format(voltage)
        
        # Read from the sensor
        ens160.temperature = aht_sensor.temperature
        ens160.humidity = aht_sensor.humidity
        aqi = ens160.aqi
        tvoc = ens160.tvoc
        eco2 = ens160.eco2
        AQI = "AQI: {} [{}]        ".format(str(aqi.value),str(aqi.rating))
        TVOC = "TVOC: {} ppb".format(str(tvoc))
        eCO2 = "eCO2: {} ppm [{}]         ".format(str(eco2.value), str(eco2.rating))
        Status = "Status: {}".format(ens160.operation)
        temperature = "Temperature: {} ".format(ens160.temperature)
        humidity = "humidity: {}".format(ens160.humidity)
        
        # ReadBMP
        pressure=bmp_sensor.pressure
        p_bar=pressure/100000
        p_mmHg=pressure/133.3224
        temperature_bmp=bmp_sensor.temperature
        bmp_tem = "Temp_bmp: {} C".format(temperature_bmp)
        bmp_pre = "Pressure: {} Pa, {} bar, {} mmHg".format(pressure,p_bar,p_mmHg)
        
        Render(tft, temp0, 10, beginy)
        Render(tft, temp1, 10, beginy + space * 1)
        Render(tft, volString, 10, beginy + space* 2)
        Render(tft, AQI, 10,beginy + space* 3)
        Render(tft, TVOC, 10, beginy + space* 4)
        Render(tft, eCO2, 10, beginy + space* 5)
        Render(tft, Status, 10, beginy + space* 6)
        Render(tft, temperature, 10, beginy + space* 7)
        Render(tft, humidity, 10, beginy + space* 8)
        Render(tft, bmp_tem, 10, beginy + space* 9)
        Render(tft, bmp_pre, 10, beginy + space* 10)
        sleep(1.0)
        if run_button.value() == 1:
            return
        
def Start(run_button):
    print("Init Display")
    tft = InitDisplay()
    print("Connect Wifi")
    ip = connectWifi(tft)
    print("Init Time")
    InitTime(ip)
    print("Init BMP280")
    bmp_sensor = InitBMP280()
    print("Init AHT21")
    aht_sensor = aht.AHT2x(common_i2c, crc=True)
    print("Init ENS160")
    ens160 = InitSensor()
    print("All Done")
    RenderScreen(tft, run_button, ens160, aht_sensor, bmp_sensor)

