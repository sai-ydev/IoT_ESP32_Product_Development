import time
from machine import I2C
from sensirion_i2c_driver import I2cConnection, MicroPythonI2cTransceiver
from sensirion_i2c_sen5x import Sen5xI2cDevice


i2c = I2C(scl=48, sda=47, freq=400000)
i2c_transceiver = MicroPythonI2cTransceiver(i2c)
device = Sen5xI2cDevice(I2cConnection(i2c_transceiver))

# Print some device information
print("Version: {}".format(device.get_version()))
print("Product Name: {}".format(device.get_product_name()))
print("Serial Number: {}".format(device.get_serial_number()))

# Perform a device reset (reboot firmware)
device.device_reset()

# Start measurement
device.start_measurement()
for _ in range(1000):
    # Wait until next result is available
    print("Waiting for new data...")
    while device.read_data_ready() is False:
        time.sleep(0.1)

    # Read measured values -> clears the "data ready" flag
    values = device.read_measured_values()
    print(values)

    # Access a specific value separately (see Sen5xMeasuredValues)
    mass_concentration = values.mass_concentration_2p5.physical
    ambient_temperature = values.ambient_temperature.degrees_celsius

    # Read device status
    status = device.read_device_status()
    print("Device Status: {}\n".format(status))

# Stop measurement
device.stop_measurement()
print("Measurement stopped.")
