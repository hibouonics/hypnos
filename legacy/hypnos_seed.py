from machine import Pin, I2C
import utime as time
from MCP7940 import MCP7940

i2c = I2C(0, sda=Pin(20,Pin.PULL_UP), scl=Pin(21,Pin.PULL_UP))

mcp = MCP7940(i2c)

mcp.time; time.localtime()


mcp.time # Read time
mcp.time = time.localtime() # Set time
mcp.start() # Start MCP oscillator
mcp.time # Read time after setting it, repeat to see time incrementing

mcp.is_battery_backup_enabled()
mcp.battery_backup_enable(1)
mcp.is_battery_backup_enabled()

mcp.time; time.localtime()

done = Pin(22, Pin.OUT)
done.low()

def read_i2c_and_split(i2c, address, register, length):
    # Read data from the I2C device
    data = i2c.readfrom_mem(address, register, length).hex()
    # Split the hexadecimal string into pairs
    split_data = ' '.join([data[i:i+2] for i in range(0, len(data), 2)])
    return split_data

def write_i2c_from_split(i2c, address, register, hex_string):
    # Remove spaces and convert the hex string to bytes
    data = bytes.fromhex(hex_string.replace(' ', ''))
    # Write the data to the specified I2C device and register
    i2c.writeto_mem(address, register, data)

def read_i2c_and_split_ascii(i2c, address, register, length):
    # Read data from the I2C device
    data = i2c.readfrom_mem(address, register, length)
    # Convert the data to an ASCII string
    ascii_string = ''.join([chr(byte) for byte in data])
    return ascii_string

def write_i2c_from_ascii(i2c, address, register, ascii_string):
    # Convert the ASCII string to bytes
    data = bytes(ascii_string, 'ascii')
    # Write the data to the specified I2C device and register
    i2c.writeto_mem(address, register, data)

def set_alarm(i2c):
    write_i2c_from_split(i2c, 0x6f, 0x7, '90')

def clear_alarm(i2c):
    write_i2c_from_split(i2c, 0x6f, 0x7, '80')

def clear_alarm_int(i2c):
    write_i2c_from_split(i2c, 0x6f, 0xd, '00')

read_i2c_and_split(i2c,0x6f,0x20,64)
read_i2c_and_split(i2c,0x6f,0xa,6)
mcp.time