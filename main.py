import sys
import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
from machine import Pin
import machine
import secrets
import st7789v

run_button = Pin(0, Pin.IN, Pin.PULL_UP)

try:
    if run_button.value() == 0:
        st7789v.Start(run_button)
except KeyboardInterrupt:
    machine.reset()