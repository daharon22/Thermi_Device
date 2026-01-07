import network
import socket
from machine import Pin, I2C, PWM, Timer
import time
import urequests as requests
from ssd1306 import SSD1306_I2C
from MAX6675 import MAX6675
from utime import sleep
import json


WIDTH =128 
HEIGHT= 64
i2c=I2C(0,scl=Pin(13),sda=Pin(12),freq=200000)
oled = SSD1306_I2C(WIDTH,HEIGHT,i2c)

sck1 = Pin(2, Pin.OUT)
cs1 = Pin(3, Pin.OUT)
so1 = Pin(4, Pin.IN)
sensor1 = MAX6675(sck1, cs1, so1)

sck2 = Pin(6, Pin.OUT)
cs2 = Pin(7, Pin.OUT)
so2 = Pin(8, Pin.IN)
sensor2 = MAX6675(sck2, cs2, so2)

buzzer = PWM(Pin(15))
buzzer.freq(500)
 
button = Pin(16, Pin.IN, Pin.PULL_UP)
buttonPressed=0
actuallyPressed=1

led1 = Pin(18, Pin.OUT)
led1.value(1)

led2 = Pin(19, Pin.OUT)
led2.value(1)

sensorOneOver = False;
sensorTwoOver = False;
ssid = '****'
password = '*****'



def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        oled.text("Waiting for", 0, 0)
        oled.text("connection...", 0, 15)
        oled.show()
        sleep(1) 
    print(wlan.ifconfig())
connect()
#except KeyboardInterrupt:
#    #machine.reset()
    

maxTemp1=30
maxTemp2=30
def postTemp (sensor):
    mydata = {'token': '12345',
        'temperature_t1': sensor1.read(),
        'temperature_t2': sensor2.read(),
        'temperature_t3': sensor1.read(),
        'event_type': sensor + ' has passed the max temp!'}
    mydata = json.dumps(mydata)
    print("gothere")
    try:
        res = requests.post(url='http://www.brydda.com:3000/api/newdeviceevent', headers = {'content-type': 'application/json'}, data = mydata).json()
    except OSError as e:
        print("error", e)
    print(res)
    
def updateTemp ():
    mydata = {'token': '12345',
        'temperature_t1': sensor1.read(),
        'temperature_t2': sensor2.read(),
        'temperature_t3': sensor1.read(),
        'event_type': 'update'}
    mydata = json.dumps(mydata)
    print("gothere")
    try:
        res = requests.post(url='http://www.brydda.com:3000/api/newdeviceevent', headers = {'content-type': 'application/json'}, data = mydata).json()
    except OSError as e:
        print("error", e)
    print(res)


def updateScreen(t):
    global sensorOneOver
    global sensorTwoOver
    
    eventProcessed = False

    if button.value()==0:
        getMaxTemps()
    oled.fill(0)
    oled.text("Temp1", 0, 0)
    oled.text(str(sensor1.read()), 0, 40)
    oled.text("Temp2", 60, 0)
    oled.text(str(sensor2.read()), 60, 40)
    oled.show()
    print(sensor1.read())
    if sensor1.read()>maxTemp1 and sensorOneOver== False:
        print("you have arrived")
        sensorOneOver=True
        eventProcessed = True
        postTemp("Sensor 1")
        
    if sensor2.read()>maxTemp2 and sensorTwoOver== False:
        sensorTwoOver=True
        eventProcessed = True
        postTemp("Sensor 2")
        
    if sensor1.read()<maxTemp1:
        sensorOneOver = False
        
    if sensor2.read()<maxTemp2:
        sensorTwoOver = False
        
    if eventProcessed==False:
        updateTemp()
        
def getMaxTemps():
    mydata = {'token': '12345'}
    mydata = json.dumps(mydata)
    try:
        res = requests.post(url='http://www.brydda.com:3000/api/getMaxTemp', headers = {'content-type': 'application/json'}, data = mydata).json()
    except OSError as e:
        print("error", e)
    print(res)
    global maxTemp1
    global maxTemp2
    maxTemp1=res['maxTemp1']
    maxTemp2=res['maxTemp2']
    print(maxTemp1)
    print(maxTemp2)
    #maxTemp1 = res.maxTemp1;
    #maxTemp2 = res.maxTemp2;



getMaxTemps()    
t=Timer()
t.init(period=1000, callback=updateScreen)
print("hello world")
print(sensor1.read())
print(button.value())
time.sleep(.5)
    

    
    





