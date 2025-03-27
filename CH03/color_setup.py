from machine import Pin, SPI
import gc
from drivers.ili93xx.ili9341 import ILI9341 as SSD

pdc = Pin(9, Pin.OUT, value=0)
prst = Pin(8, Pin.OUT, value=1)
pcs = Pin(10, Pin.OUT, value=1)
spi = SPI(1, sck=Pin(39), mosi=Pin(42), miso=Pin(21), baudrate=10_000_000)

gc.collect()  # Precaution before instantiating framebuf

ssd = SSD(spi, cs=pcs, dc=pdc, rst=prst)