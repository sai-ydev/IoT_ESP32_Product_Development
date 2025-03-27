from machine import Pin
import time

BUILTIN_LED = 13

led = Pin(BUILTIN_LED, Pin.OUT)
while True:
  led.on()
  time.sleep(1)
  led.off()
  time.sleep(1)