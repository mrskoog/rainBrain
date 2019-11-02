import Adafruit_BMP.BMP085 as BMP085
from gpiozero import InputDevice
import datetime
import csv
import time

baro_sensor = BMP085.BMP085()
rain_sensor = InputDevice(pin=4, pull_up=True)
rain_since_last_time = False

def logg_data_now():
    print("Logging " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    with open("weather_data.csv", 'a') as csv_file:
        global rain_since_last_time
        writer = csv.writer(csv_file)
        rain = 1 if rain_since_last_time else 0
        pressure = 0
        for i in range(5):
            pressure += baro_sensor.read_pressure()
        pressure = pressure / 5

        data = [rain,
                baro_sensor.read_temperature(),
                pressure,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M")]
        writer.writerow(data)
        rain_since_last_time = False


print("*** starting rain logger ***")
old_time = 0

while True:
    if rain_sensor.is_active:
        rain_since_last_time = True
    if time.time() - old_time > 1800:
  	old_time = time.time()
        logg_data_now()
    time.sleep(10)
