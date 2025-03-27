import urequests
import network
import time
import secrets

url = "https://www.airnowapi.org/aq/observation/zipCode/current/?"

parameters = {
    "format" : "application/json",
    "API_KEY" : secrets.API_KEY
}

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)

while not wlan.isconnected():
    print(".")
    time.sleep(1)
    
print(f"Success! Connected to {secrets.SSID}")
network_params = wlan.ifconfig()
print(f"IP address is {network_params[0]}")

parameters["zipCode"] = input("Enter a valid zipcode: ")
parameters["distance"] = input("Enter distance radius: ")

for key, value in parameters.items():
    url += key + "=" + value + "&"

url = url.rstrip("&")
print(f"The URL is {url}")

try:
    response = urequests.get(url)
except Exception as error:
    print(error)
else:
    print(response.status_code)
    print(response.json())
finally:
    wlan.disconnect()