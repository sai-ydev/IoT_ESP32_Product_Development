import network


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
networks = wlan.scan()

for data in networks:
    name, _, _, rssi, _, _ = data
    decoded_name = name.decode("utf-8")
    print(f"Network: {decoded_name}, S.Strength: {rssi}dBm")
    