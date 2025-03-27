
import bluetooth
import random
import struct
import time
from ble_advertising import advertising_payload
from machine import I2C
from lsm6ds3 import LSM6DS3, NORMAL_MODE_104HZ
from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_INDICATE_DONE = const(20)

_FLAG_READ = const(0x0002)
_FLAG_NOTIFY = const(0x0010)
_FLAG_INDICATE = const(0x0020)

# org.bluetooth.service.fitness_machine
_FIT_SENSE_UUID = bluetooth.UUID(0x1826)
# org.bluetooth.characteristic.step_counter_activity.summary
_FIT_CHAR = (
    bluetooth.UUID(0x2B40),
    _FLAG_READ | _FLAG_NOTIFY | _FLAG_INDICATE,
)
_FIT_SENSE_SERVICE = (
    _FIT_SENSE_UUID,
    (_FIT_CHAR,),
)

# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_WALKING_SENSOR = const(1091)

i2c = I2C(1, scl=48, sda=47, freq=400000)
lsm6ds3 = LSM6DS3(i2c, mode=NORMAL_MODE_104HZ)

lsm6ds3.reset_step_count()

class BLEStepCounter:
    def __init__(self, ble, name="step-counter"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle,),) = self._ble.gatts_register_services((_FIT_SENSE_SERVICE,))
        self._connections = set()
        self._payload = advertising_payload(
            name=name, services=[_FIT_SENSE_UUID], appearance=_ADV_APPEARANCE_WALKING_SENSOR
        )
        self._advertise()

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_INDICATE_DONE:
            conn_handle, value_handle, status = data

    def set_step_count(self, step_count, notify=False, indicate=False):
        # Data is sint16 in degrees Celsius with a resolution of 0.01 degrees Celsius.
        # Write the local value, ready for a central to read.
        self._ble.gatts_write(self._handle, struct.pack("<h", step_count))
        if notify or indicate:
            for conn_handle in self._connections:
                if notify:
                    # Notify connected centrals.
                    self._ble.gatts_notify(conn_handle, self._handle)
                if indicate:
                    # Indicate connected centrals.
                    self._ble.gatts_indicate(conn_handle, self._handle)

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)


def demo():
    ble = bluetooth.BLE()
    step_counter = BLEStepCounter(ble)

    i = 0

    while True:
        # Write every second, notify every 10 seconds.
        i = (i + 1) % 10
        steps = lsm6ds3.get_step_count()
        print("Steps: {}".format(steps))
        step_counter.set_step_count(steps, notify=(i == 0), indicate=False)
        time.sleep_ms(1000)


if __name__ == "__main__":
    demo()