import utime
import network
import secrets
from lora.sx127x import SX1276
from machine import Pin, SPI
import network
import urequests

IO_FEED_ID = ""

parameters = {
    "Content-Type" : "application/json",
}

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)

while not wlan.isconnected():
    print(".")
    utime.sleep(1)
    
print(f"Success! Connected to {secrets.SSID}")
network_params = wlan.ifconfig()
print(f"IP address is {network_params[0]}")

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

def get_modem(): 
    lora_cfg = {
        "freq_khz": 916000,
        "sf": 8,
        "bw": "500",  # kHz
        "coding_rate": 8,
        "preamble_len": 12,
        "output_power": 0,  # dBm
    }
    
    return SX1276(
        spi=SPI(1, baudrate=2000_000, polarity=0, phase=0,
                miso=Pin(12), mosi=Pin(11), sck=Pin(13)),
        cs=Pin(10),
        dio0=Pin(8),
        reset=Pin(9),
        lora_cfg=lora_cfg,
    )

def main():
    modem = get_modem()
    while True:
        rx_message = modem.recv(timeout_ms=10000)
        if rx_message:
            message = rx_message.decode("utf-8")
            if "Steps:" in message:
                idx = message.index(":")
                steps = int(message[idx+1:])
                if steps >= 0:
                    post_data(IO_FEED_ID, str(steps))
                    
                    

if __name__ == "__main__":
    main()