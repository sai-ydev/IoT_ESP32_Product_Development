import time
import bluetooth
from micropython import const

_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_ADV_TYPE_NAME = const(9)

SCAN_DURATION = 1000

def decode_field(payload, adv_type):
    i = 0
    result = []
    while i + 1 < len(payload):
        if payload[i + 1] == adv_type:
            result.append(payload[i + 2 : i + payload[i] + 1])
        i += 1 + payload[i]
    return result

def decode_name(payload):
    n = decode_field(payload, _ADV_TYPE_NAME)
    return str(n[0], "utf-8") if n else ""

def irq_callback(event, data):
  if event == _IRQ_SCAN_RESULT:
    _, addr, _, _, ad_data = data
    name = decode_name(ad_data)
    formatted_addr = ":".join(["0x{:02X}".format(i) for i in addr])
    print(name, formatted_addr)
  elif event == _IRQ_SCAN_DONE:
    print("Scan Complete")



ble = bluetooth.BLE()
ble.active(True)
ble.irq(irq_callback)
ble.gap_scan(SCAN_DURATION, 30000, 30000)
# wait for scan to finish
time.sleep_ms(SCAN_DURATION * 2)