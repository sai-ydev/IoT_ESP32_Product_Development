import network
import time

ssid = "mywifi"
password = "password"
wlan = network.WLAN(network.STA_IF)
wlan.active(True)


wlan.connect(ssid, password)

while not wlan.isconnected():
    print(".")
    time.sleep(1)

print(f"Success! Connected to {ssid}")
network_params = wlan.ifconfig()

print(f"IP address is {network_params[0]}")

wlan.disconnect()