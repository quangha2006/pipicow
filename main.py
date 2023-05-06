import ntptime
import utime
from time import sleep
from picozero import pico_temp_sensor, pico_led
from machine import Pin, SPI, I2C, ADC
import machine
import config
import st7789v
from WifiConnect import WIFI
from st7789v import TFTDisplay
from ds3231_port import DS3231
from PiicoDev_ENS160 import PiicoDev_ENS160
import aht
from bmp280 import BMP280
import bmp280
import Utils

common_scl = Pin(5)
common_sda = Pin(4)
common_freq = 100000
common_id = 0
common_i2c = I2C(id=common_id, scl=common_scl,
                 sda=common_sda, freq=common_freq)

run_button = Pin(0, Pin.IN, Pin.PULL_UP)

analogIn0 = ADC(Pin(26, mode=Pin.IN))
analogIn4 = ADC(4)


def InitDisplay():
    BACKLIGHT_PIN = 10
    RESET_PIN = 11
    DC_PIN = 12
    CS_PIN = 13
    CLK_PIN = 14
    DIN_PIN = 15
    spi = SPI(1, baudrate=40000000, sck=Pin(CLK_PIN), mosi=Pin(DIN_PIN))
    reset = Pin(RESET_PIN, Pin.OUT)
    cs = Pin(CS_PIN, Pin.OUT)
    dc = Pin(DC_PIN, Pin.OUT)
    backlight = Pin(BACKLIGHT_PIN, Pin.OUT)
    tft = TFTDisplay(spi, 240, 320, dc=dc, reset=reset,
                     cs=cs, backlight=backlight, rotation=4)
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

    rtc = machine.RTC()
    utcNow = utime.time()

    # 7 hours = 25200 seconds# for gmt. For me gmt+7.
    gmt = utcNow+25200

    # for second to convert time
    (year, month, mday, hour, minute, second,
     weekday, yearday) = utime.localtime(gmt)
    # first 0 = week of year
    # second 0 = milisecond
    rtc.datetime((year, month, mday, 0, hour, minute, second, 0))
    return ds3231


def InitScreen(display):
    display.FillBlack()
    # Screen not change
    display.RenderRec(0, 0, 240, 32, [134, 156, 152])
    display.Render("QUANG HA", 60, 0, "LB", color=[
                   255, 255, 255], bg=[134, 156, 152])


def loop(display, wifi, ens160_sensor, aht_sensor, bmp_sensor, ds3231):
    begin_ms = utime.ticks_ms()
    beginy = 100
    space = 18
    currentTime = utime.localtime()
    # format: web, 25 May, 2023
    date_string = "{},{} {},{}".format(Utils.WeekFromInt(
        currentTime[6]), currentTime[2], Utils.MonthFromInt(currentTime[1]), currentTime[0])
    time_string = "{:02}:{:02}:{:02}".format(
        currentTime[3], currentTime[4], currentTime[5])
    year_string = "{}".format(currentTime[0])

    # Render(tft, year_string, 120, 138, font_M)
    temp0 = "Temp0: {}".format(ds3231.get_temperature())

    ADC_voltage = analogIn4.read_u16() * (3.3 / (65535))
    temperature_celcius = 27 - (ADC_voltage - 0.706)/0.001721
    temp1 = "Temp1: {:.2f}".format(temperature_celcius)

    sensorValue = analogIn0.read_u16()
    voltage = sensorValue * (3.3 / 65535) * 5.0
    volString = "Voltage: {:.2f}".format(voltage)

    # Read from the sensor
    ens160_sensor.temperature = aht_sensor.temperature
    ens160_sensor.humidity = aht_sensor.humidity
    aqi = ens160_sensor.aqi
    tvoc = ens160_sensor.tvoc
    eco2 = ens160_sensor.eco2
    AQI = "AQI: {} [{}]        ".format(str(aqi.value), str(aqi.rating))
    TVOC = "TVOC: {} ppb".format(str(tvoc))
    eCO2 = "eCO2: {} ppm [{}]         ".format(
        str(eco2.value), str(eco2.rating))
    Status = "Status: {}".format(ens160_sensor.operation)
    temperature = "Temperature: {} ".format(ens160_sensor.temperature)
    humidity = "humidity: {}".format(ens160_sensor.humidity)

    # ReadBMP
    pressure = bmp_sensor.pressure
    p_bar = pressure/100000
    p_mmHg = pressure/133.3224
    temperature_bmp = bmp_sensor.temperature
    bmp_tem = "Temp_bmp: {} C".format(temperature_bmp)
    bmp_pre = "Pressure: {} Pa, {} bar, {} mmHg".format(
        pressure, p_bar, p_mmHg)

    display.Render(time_string, 60, 38, "LB", [81, 207, 102])
    display.Render(date_string, 0, 78, "M")
    display.Render(temp0, 10, beginy)
    display.Render(temp1, 10, beginy + space * 1)
    display.Render(volString, 10, beginy + space * 2)
    display.Render(AQI, 10, beginy + space * 3)
    display.Render(TVOC, 10, beginy + space * 4)
    display.Render(eCO2, 10, beginy + space * 5)
    display.Render(Status, 10, beginy + space * 6)
    display.Render(temperature, 10, beginy + space * 7)
    display.Render(humidity, 10, beginy + space * 8)
    display.Render(bmp_tem, 10, beginy + space * 9)
    display.Render(bmp_pre, 10, beginy + space * 10)
    end_ms = utime.ticks_ms()
    runningTime = end_ms - begin_ms
    utime.sleep_ms(1000 - runningTime)
    if run_button.value() == 1:
        return


try:
    if run_button.value() == 0:
        print("Init Display")
        display = InitDisplay()
        InitScreen(display)
        print("Connect Wifi")
        wifi = WIFI(config.ssid, config.password)
        print("Init Time")
        ds3231 = InitTime(wifi)
        print("Init BMP280")
        bmp_sensor = InitBMP280()
        print("Init AHT21")
        aht_sensor = InitAHT21()
        print("Init ENS160")
        ens160_sensor = InitENS160()
        print("All Done")
        while (run_button.value() == 0):
            loop(display, wifi, ens160_sensor, aht_sensor, bmp_sensor, ds3231)

except KeyboardInterrupt:
    machine.reset()
