import utime # for delays
# display related imports
from color_setup import ssd  # Create a display instance
from gui.core.nanogui import refresh
from gui.widgets.meter import Meter
from gui.widgets.label import Label
import gui.fonts.arial10 as arial10
from gui.core.writer import Writer, CWriter
from gui.core.colors import *
# sensor related imports
from machine import I2C
from sensirion_i2c_driver import MicroPythonI2cTransceiver, I2cConnection
from sensirion_i2c_scd import Scd4xI2cDevice
from sensirion_i2c_sen5x import Sen5xI2cDevice

i2c = I2C(scl=48, sda=47, freq=400000)
i2c_transceiver = MicroPythonI2cTransceiver(i2c)
scd4x = Scd4xI2cDevice(I2cConnection(i2c_transceiver))
sen5x = Sen5xI2cDevice(I2cConnection(i2c_transceiver))

scd4x.stop_periodic_measurement()
print("scd4x Serial Number: {}".format(scd4x.read_serial_number()))
scd4x.start_periodic_measurement()

print("Version: {}".format(sen5x.get_version()))
print("Product Name: {}".format(sen5x.get_product_name()))
print("Serial Number: {}".format(sen5x.get_serial_number()))

sen5x.device_reset()
sen5x.start_measurement()

refresh(ssd, True)

CWriter.set_textpos(ssd, 0, 0)  # In case previous tests have altered it
wri = CWriter(ssd, arial10, GREEN, BLACK, verbose=False)
wri.set_clip(True, True, False)

co2_meter = Meter(wri, 5, 2, height = 80, divisions = 40, ptcolor=YELLOW,
              label='', style=Meter.BAR, legends=('400', '2300', '5000'))

voc_meter = Meter(wri, 5, 102, height = 80, divisions = 40, ptcolor=YELLOW,
              label='', style=Meter.BAR, legends=('0', '250', '500'))

p25_meter = Meter(wri, 5, 202, height = 80, divisions = 40, ptcolor=YELLOW,
              label='', style=Meter.BAR, legends=('0', '50.0', '100.0'))

co2_data_width = wri.stringlen('0000 ppm')
co2_label = Label(wri, 100, 0, 'C02:')
co2_value_label = Label(wri, 100, 25, co2_data_width, bdcolor=YELLOW)

voc_index_width = wri.stringlen('000')
voc_label = Label(wri, 100, 100, 'VOC:')
voc_value_label = Label(wri, 100, 127, co2_data_width, bdcolor=YELLOW)

p25_index_width = wri.stringlen('000.0 ug/m^3')
p25_label = Label(wri, 100, 200, 'P2.5:')
p25_value_label = Label(wri, 100, 230, co2_data_width, bdcolor=YELLOW)

def meter_update(meter, update_value):
    meter.value(update_value)
    refresh(ssd)

def label_update(label, update_value):
    label.value(update_value)
    refresh(ssd)
  

while True:
    print("Waiting for new SCD4x data...")
    while scd4x.get_data_ready_status() is False:
        utime.sleep(0.1)
    co2, temperature, humidity = scd4x.read_measurement()
    scaled_co2 = (co2.co2 - 400) / 4600
    meter_update(co2_meter, scaled_co2)
    label_update(co2_value_label, "{0} ppm".format(co2.co2))
    # use default formatting for printing output:
    print("{}, {}, {}".format(co2, temperature, humidity))
    
    print("Waiting for new SEN5x data...")
    while sen5x.read_data_ready() is False:
        time.sleep(0.1)
       
    # Read measured values -> clears the "data ready" flag
    sen5x_values = sen5x.read_measured_values()
    print(sen5x_values)
    voc_value = sen5x_values.voc_index.scaled
    p25_concentration = sen5x_values.mass_concentration_2p5.physical
    p25_update = p25_concentration / 100
    voc_update = (voc_value) / 500
    meter_update(voc_meter, voc_update)
    meter_update(p25_meter, p25_update)
    label_update(voc_value_label, "{0}".format(voc_value))
    label_update(p25_value_label, "{0}".format(p25_concentration))
    
