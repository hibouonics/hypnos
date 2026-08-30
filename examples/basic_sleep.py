"""Schedule a five-second wake-up using Hibouonics Hypnos."""

from machine import I2C, Pin
from hypnos import Hypnos


i2c = I2C(0, sda=Pin(20, Pin.PULL_UP), scl=Pin(21, Pin.PULL_UP))
done = Pin(22, Pin.OUT)
done.value(0)

hypnos = Hypnos(i2c, done)
hypnos.start()
print("Current RTC time:", hypnos.time)
hypnos.sleep((0, 0, 0, 0, 5))
