
import bluetooth
import aioble
import asyncio
import struct
import time
from ble_advertising import advertising_payload
from machine import I2C
from lsm6ds3 import LSM6DS3, NORMAL_MODE_104HZ
from micropython import const

# org.bluetooth.service.fitness_machine
_FIT_SENSE_UUID = bluetooth.UUID(0x1826)
# org.bluetooth.characteristic.step_counter_activity.summary
_FIT_CHAR = bluetooth.UUID(0x2B40)

# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_WALKING_SENSOR = const(1091)

# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 250_000

i2c = I2C(1, scl=48, sda=47, freq=400000)
lsm6ds3 = LSM6DS3(i2c, mode=NORMAL_MODE_104HZ)

lsm6ds3.reset_step_count()

# Register GATT server.
fitness_service = aioble.Service(_FIT_SENSE_UUID)
step_count_characteristic = aioble.Characteristic(
    fitness_service, _FIT_CHAR, read=True, notify=True
)
aioble.register_services(fitness_service)

def _encode_step_count(step_count):
    return struct.pack("<h", step_count)

# This would be periodically polling a hardware sensor.
async def sensor_task():
    while True:
        steps = lsm6ds3.get_step_count()
        print("Steps: {}".format(steps))
        step_count_characteristic.write(_encode_step_count(steps), send_update=True)
        await asyncio.sleep_ms(1000)
        
async def peripheral_task():
    while True:
        async with await aioble.advertise(
            _ADV_INTERVAL_MS,
            name="step-counter",
            services=[_FIT_SENSE_UUID],
            appearance=_ADV_APPEARANCE_WALKING_SENSOR,
        ) as connection:
            print("Connection from", connection.device)
            await connection.disconnected(timeout_ms=None)

def pedometer_demo():
    t1 = asyncio.create_task(sensor_task())
    t2 = asyncio.create_task(peripheral_task())
    await asyncio.gather(t1, t2)


if __name__ == "__main__":
    asyncio.run(pedometer_demo())