from OLED_1inch3 import OLED_1inch3
from machine import Pin,SPI
import framebuf
import time
          
#if __name__=='__main__':

    OLED = OLED_1inch3()
#     OLED.fill(0x0000) 
#     OLED.show()
#     OLED.rect(0,0,128,64,OLED.white)
#     time.sleep(0.5)
#     OLED.show()
#     OLED.rect(10,22,20,20,OLED.white)
#     time.sleep(0.5)
#     OLED.show()
#     OLED.fill_rect(40,22,20,20,OLED.white)
#     time.sleep(0.5)
#     OLED.show()
#     OLED.rect(70,22,20,20,OLED.white)
#     time.sleep(0.5)
#     OLED.show()
#     OLED.fill_rect(100,22,20,20,OLED.white)
#     time.sleep(0.5)
#     OLED.show()
#     time.sleep(1)
#     
#     OLED.fill(0x0000)
#     OLED.line(0,0,5,64,OLED.white)
#     OLED.show()
#     time.sleep(0.01)
#     OLED.line(0,0,20,64,OLED.white)
#     OLED.show()
#     time.sleep(0.01)
#     OLED.line(0,0,35,64,OLED.white)
#     OLED.show()
#     time.sleep(0.01)
#     OLED.line(0,0,65,64,OLED.white)
#     OLED.show()
#     time.sleep(0.01)
#     OLED.line(0,0,95,64,OLED.white)
#     OLED.show()
#     time.sleep(0.01)
#     OLED.line(0,0,125,64,OLED.white)
#     OLED.show()
#     time.sleep(0.01)
#     OLED.line(0,0,125,41,OLED.white)
#     OLED.show()
#     time.sleep(0.1)
#     OLED.line(0,0,125,21,OLED.white)
#     OLED.show()
#     time.sleep(0.01)
#     OLED.line(0,0,125,3,OLED.white)
#     OLED.show()
#     time.sleep(0.01)
#     
#     OLED.line(127,1,125,64,OLED.white)
#     OLED.show()
#     time.sleep(0.01)
#     OLED.line(127,1,110,64,OLED.white)
#     OLED.show()
#     time.sleep(0.01)
#     OLED.line(127,1,95,64,OLED.white)
#     OLED.show()
#     time.sleep(0.01)
#     OLED.line(127,1,65,64,OLED.white)
#     OLED.show()
#     time.sleep(0.01)
#     OLED.line(127,1,35,64,OLED.white)
#     OLED.show()
#     time.sleep(0.01)
#     OLED.line(127,1,1,64,OLED.white)
#     OLED.show()
#     time.sleep(0.01)
#     OLED.line(127,1,1,44,OLED.white)
#     OLED.show()
#     time.sleep(0.01)
#     OLED.line(127,1,1,24,OLED.white)
#     OLED.show()
#     time.sleep(0.01)
#     OLED.line(127,1,1,3,OLED.white)
#     OLED.show()
#     time.sleep(1)
keyA = Pin(15,Pin.IN,Pin.PULL_UP)
keyB = Pin(17,Pin.IN,Pin.PULL_UP)
OLED.fill(0x0000) 
OLED.text("128 x 64 Pixels",1,10,OLED.white)
OLED.text("Pico-OLED-1.3",1,27,OLED.white)
OLED.text("SH1107",1,44,OLED.white)  
OLED.show()

loop = 1
while(loop):
    if keyA.value() == 0 or keyB.value() == 0:
        OLED.fill(0x0000)
        OLED.show()
        loop = 0
        
        
        
    
#     time.sleep(1)
#     OLED.fill(0x0000) 
#     keyA = Pin(15,Pin.IN,Pin.PULL_UP)
#     keyB = Pin(17,Pin.IN,Pin.PULL_UP)
#     while(1):
#         if keyA.value() == 0:
#             OLED.fill_rect(0,0,128,20,OLED.white)
#             print("A")
#         else :
#             OLED.fill_rect(0,0,128,20,OLED.black)
#             
#             
#         if(keyB.value() == 0):
#             OLED.fill_rect(0,44,128,20,OLED.white)
#             print("B")
#         else :
#             OLED.fill_rect(0,44,128,20,OLED.black)
#         OLED.fill_rect(0,22,128,20,OLED.white)
#         OLED.text("press the button",0,28,OLED.black)
#             
#         OLED.show()
    
    
#     time.sleep(1)
#     OLED.fill(0xFFFF)
