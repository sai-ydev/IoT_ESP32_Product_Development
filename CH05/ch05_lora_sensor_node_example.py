import utime
from machine import Pin, SPI, I2C
from lora.sx127x import SX1276
from lsm6ds3 import LSM6DS3, NORMAL_MODE_104HZ

def init_imu():
    i2c = I2C(0, scl=48, sda=47)
    return LSM6DS3(i2c, mode=NORMAL_MODE_104HZ)
    
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
    imu = init_imu()
    
    while True:
        steps = imu.get_step_count()
        print("Steps = {}".format(steps))
        modem.send("Steps:{}".format(steps))
        utime.sleep(10)

if __name__ == "__main__":
    main()