import bluetooth
from ble_advertising import advertising_payload # used from micropython repo
from micropython import const
import machine
import lsm6ds3
import ustruct
import utime

# ble connection states
central_connect = const(1)
central_disconnect = const(2)
indicate_done = const(20)

# flags
read_flag = const(0x0002)
notify_flag = const(0x0010)
indicate_flag = const(0x0020)

# org.bluetooth.service.fitness_machine
pedometer_uuid = bluetooth.UUID(0x1826)
# org.bluetooth.characteristic.step_counter_activity.summary
pedometer_characteristic = (
    bluetooth.UUID(0x2B40),
    read_flag | notify_flag | indicate_flag,
)
pedometer_service = (
    pedometer_uuid,
    (pedometer_characteristic,),
)

# org.bluetooth.characteristic.gap.appearance.xml
pedometer_appearance = const(1091)

i2c = machine.I2C(1, scl=48, sda=47, freq=400000)
pedometer = lsm6ds3.LSM6DS3(i2c, mode=lsm6ds3.NORMAL_MODE_104HZ)

pedometer.reset_step_count()

class ESP32Pedometer:
    def __init__(self, ble_connection, name="step-counter"):
        self.ble_conn = ble_connection
        self.ble_conn.active(True)
        self.ble_conn.irq(self.irq_handler)
        ((self.handle,),) = self.ble_conn.gatts_register_services((pedometer_service,))
        self.connections = set()
        self.payload = advertising_payload(
            name=name, services=[pedometer_uuid], appearance=pedometer_appearance
        )
        self.advertise()

    def irq_handler(self, event, data):
        
        if event == central_connect:
            conn_handle, _, _ = data
            self.connections.add(conn_handle)
        elif event == central_disconnect:
            conn_handle, _, _ = data
            self.connections.remove(conn_handle)
            self.advertise()
        elif event == indicate_done:
            conn_handle, value_handle, status = data

    def set_step_count(self, step_count, notify=False, indicate=False):
        self.ble_conn.gatts_write(self.handle, ustruct.pack("<h", step_count))
        if notify or indicate:
            for conn_handle in self.connections:
                if notify:
                    self.ble_conn.gatts_notify(conn_handle, self.handle)
                if indicate:
                    self.ble_conn.gatts_indicate(conn_handle, self._handle)

    def advertise(self, interval_us=500000):
        # advertise with 500ms interval
        self.ble_conn.gap_advertise(interval_us, adv_data=self.payload)


def demo():
    ble = bluetooth.BLE()
    step_counter = ESP32Pedometer(ble)

    i = 0

    while True:
        i = (i + 1) % 10
        steps = pedometer.get_step_count()
        print("Steps: {}".format(steps))
        step_counter.set_step_count(steps, notify=(i == 0), indicate=False)
        utime.sleep_ms(1000)


if __name__ == "__main__":
    demo()