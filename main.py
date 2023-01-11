import sys
import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine

ssid = 'YOUR_SSID'
password = 'YOUR_PASSWORD'

def systemInfo():
    print(sys.implementation)
    
def connect():
    #Connect to WLAN
    ip = ''
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    wait = 50
    wlanstatus = None
    wlanNewStatus = None
    while wlan.isconnected() == False and wait >= 0:
        if wait % 2 == 0:
            pico_led.on()
        else:
            pico_led.off()
        wlanNewStatus = wlan.status()
        if wlanstatus != wlanNewStatus:
            wlanstatus = wlanNewStatus
            print('Waiting for connection...')
        if wlanNewStatus < 0 or wlanNewStatus >= 3:
            break
        wait -= 1
        sleep(0.2)
    # Handle connection error
    if wlan.isconnected() == False:
        print('wifi connection failed!')
    else:
        print('Connected to SSID..:', ssid)
        print('IPv4 Address.......:', wlan.ifconfig()[0])
        print('Subnet Mask........:', wlan.ifconfig()[1])
        print('Default Gateway....:', wlan.ifconfig()[2])
        ip = wlan.ifconfig()[0]
    return ip
    
def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def serve(connection):
    #Start a web server
    state = 'OFF'
    pico_led.on()
    temperature = 0
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/lighton?':
            pico_led.on()
            state = 'ON'
        elif request =='/lightoff?':
            pico_led.off()
            state = 'OFF'
        temperature = pico_temp_sensor.temp
        html = webpage(temperature, state)
        client.send(html)
        client.close()

def webpage(temperature, state):
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <form action="./lighton">
            <input type="submit" value="Light on" />
            </form>
            <form action="./lightoff">
            <input type="submit" value="Light off" />
            </form>
            <p>LED is {state}</p>
            <p>Temperature is {temperature}</p>
            </body>
            </html>
            """
    return str(html)

try:
    ip = connect()
    if ip != '':
        connection = open_socket(ip)
        serve(connection)
except KeyboardInterrupt:
    machine.reset()
