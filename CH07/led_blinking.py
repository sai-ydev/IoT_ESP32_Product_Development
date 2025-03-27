from time import sleep
from machine import Pin

led = Pin(23, Pin.OUT)

while True:
    led.value(1)
    sleep(1)
    led.value(0)
    sleep(1)