import asyncio
import aioble
import bluetooth
import ustruct
import network
import utime
import creds
import urequests

# org.bluetooth.service.fitness_machine
_FIT_MACHINE_UUID = bluetooth.UUID(0x1826)
# org.bluetooth.characteristic.step_counter_activity.summary
_STEP_COUNTER_UUID = bluetooth.UUID(0x2B40)

IO_FEED_ID = "gXT3GmsDGuzkuZfF1Hg8M4jYpYa5"

parameters = {
    "Content-Type" : "application/json",
}

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
print(wifi.scan())
wifi.connect(creds.SSID, creds.PASSWORD)

while not wifi.isconnected():
    print(".")
    utime.sleep(1)
    
print(f"Success! Connected to {creds.SSID}")
network_params = wifi.ifconfig()
print(f"IP address is {network_params[0]}")

def parse_step_count(data):
    return ustruct.unpack("<h", data)[0]


async def connect_step_counter():
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for scan_device in scanner:
            # See if it matches our name and the fitnesss machine service.
            if scan_device.name() == "step-counter" and _FIT_MACHINE_UUID in scan_device.services():
                return scan_device.device
    return None


async def bluetooth_client_task():
    pedometer = await connect_step_counter()
    if pedometer is None:
        print("Step Counter not found")
        return

    try:
        connection = await pedometer.connect()
    except Exception:
        print("Timeout during connection")
        return

    async with connection:
        try:
            fitness_service = await connection.service(_FIT_MACHINE_UUID)
            step_count_rx = await fitness_service.characteristic(_STEP_COUNTER_UUID)
        except asyncio.TimeoutError:
            print("Timeout discovering services/characteristics")
            return

        while connection.is_connected():
            step_count = parse_step_count(await step_count_rx.read())
            print("Step Count: {0}".format(step_count))
            post_data(IO_FEED_ID, str(step_count))
            await asyncio.sleep_ms(10000)
            
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
