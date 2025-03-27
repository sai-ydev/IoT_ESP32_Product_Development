import sys
from micropython import const
import asyncio
import aioble
import bluetooth
import random
import struct
import network
import utime
import secrets
import urequests
import machine

# org.bluetooth.service.fitness_machine
_FIT_MACHINE_UUID = bluetooth.UUID(0x1826)
# org.bluetooth.characteristic.step_counter_activity.summary
_STEP_COUNTER_UUID = bluetooth.UUID(0x2B40)

IO_FEED_ID = "gXT3GmsDGuzkuZfF1Hg8M4jYpYa5"

parameters = {
    "Content-Type" : "application/json",
}

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print(wlan.scan())
wlan.connect(secrets.SSID, secrets.PASSWORD)

while not wlan.isconnected():
    print(".")
    utime.sleep(1)
    
print(f"Success! Connected to {secrets.SSID}")
network_params = wlan.ifconfig()
print(f"IP address is {network_params[0]}")

# Helper to decode the step count.
def _decode_step_count(data):
    return struct.unpack("<h", data)[0]


async def find_step_sensor():
    # Scan for 5 seconds, in active mode, with very low interval/window (to
    # maximise detection rate).
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            # See if it matches our name and the fitnesss machine service.
            if result.name() == "step-counter" and _FIT_MACHINE_UUID in result.services():
                return result.device
    return None


async def bluetooth_client_task():
    device = await find_step_sensor()
    if not device:
        print("Step Counter not found")
        return

    try:
        print("Connecting to", device)
        connection = await device.connect()
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return

    async with connection:
        try:
            fitness_service = await connection.service(_FIT_MACHINE_UUID)
            step_count_characteristic = await fitness_service.characteristic(_STEP_COUNTER_UUID)
        except asyncio.TimeoutError:
            print("Timeout discovering services/characteristics")
            return

        while connection.is_connected():
            step_count = _decode_step_count(await step_count_characteristic.read())
            print("Step Count: {0}".format(step_count))
            post_data(IO_FEED_ID, str(step_count))
            await machine.deepsleep(10000)
            
def post_data(feed_id, data):
    url = 'https://io.adafruit.com/api/v2/webhooks/feed/'
    url += feed_id + "/?"
    for key, value in parameters.items():
        url += key + "=" + value + "&"
    url += "value=" + data

    try:
        response = urequests.post(url)
    except Exception as error:
        print(error)
    else:
        if response.status_code == 200:
            print(response.json())
        else:
            print(response.reason)


if __name__ == "__main__":
    asyncio.run(bluetooth_client_task())
