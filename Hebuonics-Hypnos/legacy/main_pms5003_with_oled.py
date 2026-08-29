import time
from machine import Pin,SPI
import framebuf          
from OLED_1inch3 import OLED_1inch3
from pms5003 import PMS5003

print("""pms5003_test.py - Continously print all data values.
""")


# Configure the PMS5003 for Enviro+
pms5003 = PMS5003(
    uart=machine.UART(1, tx=machine.Pin(4), rx=machine.Pin(5), baudrate=9600),
    pin_enable=machine.Pin(3),
    pin_reset=machine.Pin(2),
    mode="active"
)

OLED = OLED_1inch3()
keyA = Pin(15,Pin.IN,Pin.PULL_UP)
keyB = Pin(17,Pin.IN,Pin.PULL_UP)
OLED.fill(0x0000)
OLED.show()

loop = True
while(loop):
    data = pms5003.read()
    print(data)
    
    # Display PMS5003 data on the OLED
    OLED.fill(0x0000)
    OLED.text(" PM1.0:  {}".format(data.data[0]),1,5,OLED.white)
    OLED.text(" PM2.5:  {}".format(data.data[1]),1,17,OLED.white)
    OLED.text("  PM10:  {}".format(data.data[2]),1,29,OLED.white)
    OLED.text(">0.3um:  {}".format(data.data[6]),1,41,OLED.white)
    OLED.text(">0.5um:  {}".format(data.data[7]),1,53,OLED.white)
#     OLED.text(" PM1.0:  {}",1,5,OLED.white)
#     OLED.text(" PM2.5:  {}",1,17,OLED.white)
#     OLED.text("  PM10:  {}",1,29,OLED.white)
#     OLED.text(">0.3um:  {}",1,41,OLED.white)
#     OLED.text(">0.5um:  {}",1,53,OLED.white)
#     OLED.text(">1.0um:",63,43,OLED.white)
#     OLED.text(">2.5um:",63,55,OLED.white)
#     OLED.text(">5.0um:",1,129,OLED.white)
#     OLED.text(">10um:",1,146,OLED.white)
    OLED.show()
    
    time.sleep(1.0)
    if keyA.value() == 0 or keyB.value() == 0:
        loop = False
