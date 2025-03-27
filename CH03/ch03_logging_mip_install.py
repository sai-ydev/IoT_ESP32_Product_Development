import mip
import secrets
import network
import time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)

while not wlan.isconnected():
    print(".")
    time.sleep(1)
    
print(f"Success! Connected to {secrets.SSID}")
network_params = wlan.ifconfig()
print(f"IP address is {network_params[0]}")

mip.install("logging")

wlan.disconnect()
