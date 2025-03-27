import time
from machine import I2C
from sensirion_i2c_driver import MicroPythonI2cTransceiver, I2cConnection
from sensirion_i2c_scd import Scd4xI2cDevice

i2c = I2C(scl=48, sda=47, freq=400000)
i2c_transceiver = MicroPythonI2cTransceiver(i2c)
scd4x = Scd4xI2cDevice(I2cConnection(i2c_transceiver))


# Make sure measurement is stopped, else we can't read serial number or
# start a new measurement
scd4x.stop_periodic_measurement()

print("scd4x Serial Number: {}".format(scd4x.read_serial_number()))

scd4x.start_periodic_measurement()

# Measure every 5 seconds for 5 minute
for _ in range(100):
    time.sleep(5)
    co2, temperature, humidity = scd4x.read_measurement()
    # use default formatting for printing output:
    print("{}, {}, {}".format(co2, temperature, humidity))

scd4x.stop_periodic_measurement()
print("Measurement stopped.")
