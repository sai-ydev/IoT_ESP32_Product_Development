from machine import SoftI2C

i2c = SoftI2C(scl=2, sda=3, freq=400000)
results = [hex(address) for address in i2c.scan()]
print("The devices on the I2C bus are:", *results)