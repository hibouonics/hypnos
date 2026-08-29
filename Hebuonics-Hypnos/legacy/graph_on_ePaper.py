from machine import Pin,SPI
from ePaper_4IN2 import EPD_4in2
from math import cos

if __name__=='__main__':
    
    # setup the display
    epd = EPD_4in2()
    x_offset = 8
    y_offset = 5
    text_size = 3
    
    # clear the display buffers
    epd.image1Gray.fill(0xff)
    epd.image4Gray.fill(0xff)
    
    epd.image4Gray.hline(0, 150, 400, epd.black)
    epd.image4Gray.vline(200, 0, 300, epd.black)
    for x in range(400):
        epd.image4Gray.pixel(x, int(-100*cos(6.28318530718/80*(x-200)))+150, epd.black)
        #epd.image4Gray.pixel(x, -(x-200)*(x-200)+150, epd.black)
    
    #epd.image4Gray.text('GRAY4 with white background',155, 111, epd.black)    
    epd.EPD_4IN2_4GrayDisplay(epd.buffer_4Gray)
    epd.Sleep()
            
    


