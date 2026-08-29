from machine import Pin, I2C
from Hypnos import Hypnos
#import utime as time
import time
import framebuf          
from OLED_1inch3 import OLED_1inch3

i2c = I2C(0, sda=Pin(20,Pin.PULL_UP), scl=Pin(21,Pin.PULL_UP))
done = Pin(22, Pin.OUT)
hypnos = Hypnos(i2c, done)

OLED = OLED_1inch3()
keyA = Pin(15,Pin.IN,Pin.PULL_UP)
keyB = Pin(17,Pin.IN,Pin.PULL_UP)
OLED.fill(0x0000)
OLED.show()

# Display time OLED
OLED.fill(0x0000)
OLED.text("{}".format(hypnos.time[:3]),1,5,OLED.white)
OLED.text("{}".format(hypnos.time[3:6]),1,17,OLED.white)
OLED.show()

# loop = 1
# while(loop):
#     time.sleep(0.5)
#     if keyA == 0:
#         loop = 0
time.sleep(1.0)
hypnos.sleep((0,0,0,0,4))




# def read_i2c_and_split(i2c, address, register, length):
#     # Read data from the I2C device
#     data = i2c.readfrom_mem(address, register, length).hex()
#     # Split the hexadecimal string into pairs
#     split_data = ' '.join([data[i:i+2] for i in range(0, len(data), 2)])
#     return split_data
# 
# def write_i2c_from_split(i2c, address, register, hex_string):
#     # Remove spaces and convert the hex string to bytes
#     data = bytes.fromhex(hex_string.replace(' ', ''))
#     # Write the data to the specified I2C device and register
#     i2c.writeto_mem(address, register, data)
# 
# def read_i2c_and_split_ascii(i2c, address, register, length):
#     # Read data from the I2C device
#     data = i2c.readfrom_mem(address, register, length)
#     # Convert the data to an ASCII string
#     ascii_string = ''.join([chr(byte) for byte in data])
#     return ascii_string
# 
# def write_i2c_from_ascii(i2c, address, register, ascii_string):
#     # Convert the ASCII string to bytes
#     data = bytes(ascii_string, 'ascii')
#     # Write the data to the specified I2C device and register
#     i2c.writeto_mem(address, register, data)
#             