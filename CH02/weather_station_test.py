from machine import UART
from dfrobot_weatherstation import DFRobot_Atmospherlum_UART
import utime

uart1 = UART(1, baudrate=115200, tx=5, rx=4)
weather_sensor = DFRobot_Atmospherlum_UART(uart1)

while True:
    print(weather_sensor.get_information(True))
    utime.sleep(1)


    