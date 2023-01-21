# document: https://www.coderdojotc.org/micropython/displays/graph/14-lcd-st7789V/#uploading-the-st7789v-python-firmware
#
from machine import Pin, SPI
import st7789

BACKLIGHT_PIN = 10 # ignore
RESET_PIN = 11     # RST
DC_PIN = 12        # DC
CS_PIN = 13        # CS
CLK_PIN = 14       # SCL
DIN_PIN = 15       # SDA

import vga1_bold_16x32 as font

spi = SPI(1, baudrate=31250000, sck=Pin(CLK_PIN), mosi=Pin(DIN_PIN))
tft = st7789.ST7789(spi, 240, 320,
    reset=Pin(RESET_PIN, Pin.OUT),
    cs=Pin(CS_PIN, Pin.OUT),
    dc=Pin(DC_PIN, Pin.OUT),
    backlight=Pin(BACKLIGHT_PIN, Pin.OUT),
    rotation=3)
tft.init()

tft.text(font, "Hello World!",10, 0, st7789.color565(255,255,255), st7789.color565(0,0,0))
tft.text(font, "Hello World!",10, 50, st7789.color565(255,0,0), st7789.color565(0,0,0))
tft.text(font, "Hello World!",10, 100, st7789.color565(0,255,0), st7789.color565(0,0,0))
tft.text(font, "Hello World!",10, 150, st7789.color565(0,0,255), st7789.color565(0,0,0))

