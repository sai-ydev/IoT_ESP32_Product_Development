import urequests
import network
import utime
import secrets
from machine import UART
from dfrobot_weatherstation import DFRobot_Atmospherlum_UART

PARAMS = ["Temp", "Humi", "Pressure"]
FEED_ID = [
    "",
    "",
    ""
]

parameters = {
    "Content-Type" : "application/json",
}

uart = UART(1, baudrate=115200, tx=5, rx=4)
weather_sensor = DFRobot_Atmospherlum_UART(uart)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)

while not wlan.isconnected():
    print(".")
    utime.sleep(1)
    
print(f"Success! Connected to {secrets.SSID}")
network_params = wlan.ifconfig()
print(f"IP address is {network_params[0]}")

def post_id(feed_id, data):
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

def main():
    while True:
        for idx, param in enumerate(PARAMS):
            data = weather_sensor.get_value(param)
            post_id(FEED_ID[idx], data)
            utime.sleep(1)
            print("-------------------------")
        utime.sleep(15)
        
if __name__ == "__main__":
    main()
    