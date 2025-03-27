import mip
import secrets
import network
import time


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print(wlan.scan())
time.sleep(5)
wlan.connect(secrets.SSID, secrets.PASSWORD)

while not wlan.isconnected():
    wlan.scan()
    print(".")
    time.sleep(10)
    
print(f"Success! Connected to {secrets.SSID}")
network_params = wlan.ifconfig()
print(f"IP address is {network_params[0]}")

mip.install("aioble")

wlan.disconnect()
wlan.active(False)
