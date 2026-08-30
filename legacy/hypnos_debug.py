from machine import Pin, I2C
from Hypnos import Hypnos
#import utime as time
import time
import framebuf          
from OLED_1inch3 import OLED_1inch3

i2c = I2C(0, sda=Pin(20,Pin.PULL_UP), scl=Pin(21,Pin.PULL_UP))
done = Pin(22, Pin.OUT)
hypnos = Hypnos(i2c, done)

#done.high()
#done.low()
hypnos.status

#p20 = Pin(20, Pin.OUT)
#p21 = Pin(21, Pin.OUT)
#p20.low()
#p21.low()
#p20.high()
#p21.high()
