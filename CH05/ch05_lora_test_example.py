# MicroPython lora simple_rxtx example - synchronous API version
# MIT license; Copyright (c) 2023 Angus Gratton
import time
from machine import Pin, SPI
from lora.sx127x import SX1276

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
    print("Initializing...")
    modem = get_modem()

    counter = 0
    while True:
        print("Sending...")
        modem.send(f"Hello world #{counter}".encode())

        print("Receiving...")
        rx = modem.recv(timeout_ms=5000)
        if rx:
            print(f"Received: {rx!r}")
        else:
            print("Timeout!")
        time.sleep(2)
        counter += 1


if __name__ == "__main__":
    main()
