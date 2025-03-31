import mip
import creds
import network
import time


wifi = network.WLAN(network.STA_IF)
wifi.active(True)
print(wifi.scan())
wifi.connect(creds.SSID, creds.PASSWORD)

while not wifi.isconnected():
    print(".")
    time.sleep(5)
    
print(f"Success! Connected to {creds.SSID}")
network_params = wifi.ifconfig()
print(f"IP address is {network_params[0]}")

mip.install("aioble")

wifi.disconnect()
wifi.active(False)


