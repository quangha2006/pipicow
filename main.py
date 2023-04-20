import ntptime
import utime
from time import sleep
from picozero import pico_temp_sensor, pico_led
from machine import Pin, SPI, I2C
import machine
import secrets
import st7789v
from WifiConnect import WIFI
from st7789v import st7789
from ds3231_port import DS3231
from PiicoDev_ENS160 import PiicoDev_ENS160
import aht
from bmp280 import BMP280
import bmp280

common_scl=Pin(5)
common_sda=Pin(4)
common_freq=100000
common_id=0
common_i2c=I2C(id=common_id,scl=common_scl, sda=common_sda, freq=common_freq)

run_button = Pin(0, Pin.IN, Pin.PULL_UP)

def InitDisplay():
    BACKLIGHT_PIN = 10
    RESET_PIN = 11
    DC_PIN = 12
    CS_PIN = 13
    CLK_PIN = 14
    DIN_PIN = 15
    spi = SPI(1, baudrate=40000000, sck=Pin(CLK_PIN), mosi=Pin(DIN_PIN))
    reset=Pin(RESET_PIN, Pin.OUT)
    cs=Pin(CS_PIN, Pin.OUT)
    dc=Pin(DC_PIN, Pin.OUT)
    backlight=Pin(BACKLIGHT_PIN, Pin.OUT)
    tft = st7789.ST7789(spi, 240, 320, dc=dc, reset=reset, cs=cs, backlight=backlight, rotation=4)
    tft.init()
    return tft

def InitBMP280():
    bmp = BMP280(common_i2c)
    bmp.use_case(bmp280.BMP280_CASE_INDOOR)
    return bmp

def InitENS160():
    return PiicoDev_ENS160(bus=common_id, scl=common_scl, sda=common_sda, freq=common_freq)

def InitAHT21():
    return aht.AHT2x(common_i2c, crc=True)

def InitTime(wifi):
    ds3231 = DS3231(common_i2c)
    if wifi.isConnected:
        ntptime.host = "1.europe.pool.ntp.org"
        ntptime.settime()
        ds3231.save_time()
    else:
        ds3231.get_time(True)
        
    rtc=machine.RTC()
    utcNow=utime.time()
    
    # 7 hours = 25200 seconds# for gmt. For me gmt+7. 
    gmt=utcNow+25200
    
    # for second to convert time
    (year, month, mday, hour, minute, second, weekday, yearday)=utime.localtime(gmt)
    # first 0 = week of year
    # second 0 = milisecond
    rtc.datetime((year, month, mday, 0, hour, minute, second, 0))

def loop(display, wifi, ens160_sensor, aht_sensor, bmp_sensor):
    print("this is loop")

try:
    if run_button.value() == 0:
        print("Init Display")
        display = InitDisplay()
        print("Connect Wifi")
        wifi = WIFI(secrets.ssid, secrets.password)
        print("Init Time")
        InitTime(wifi)
        print("Init BMP280")
        bmp_sensor = InitBMP280()
        print("Init AHT21")
        aht_sensor = InitAHT21()
        print("Init ENS160")
        ens160_sensor = InitENS160()
        print("All Done")

        while (run_button.value() == 0):
            loop(display, wifi, ens160_sensor, aht_sensor, bmp_sensor)

except KeyboardInterrupt:
    machine.reset()