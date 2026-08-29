"""Print Hypnos RTC, alarm, and power-fail status."""

from machine import I2C, Pin
from hypnos import Hypnos


i2c = I2C(0, sda=Pin(20, Pin.PULL_UP), scl=Pin(21, Pin.PULL_UP))
done = Pin(22, Pin.OUT)
hypnos = Hypnos(i2c, done)
hypnos.print_status()
