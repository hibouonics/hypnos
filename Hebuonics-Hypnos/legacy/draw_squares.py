from machine import Pin,SPI
from ePaper_4IN2 import EPD_4in2

if __name__=='__main__':
    
    # setup the display
    epd = EPD_4in2()
    x_offset = 8
    y_offset = 5
    text_size = 3
    
    # clear the display buffers
    epd.image1Gray.fill(0xff)
    epd.image4Gray.fill(0xff)
    
    for r in range(30):
        if (r%2==0):
            for c in range(0,40,2):
                epd.image4Gray.fill_rect(10*c,10*r,10,10,epd.black)
            epd.image4Gray.text(str(r%10),1, 10*r+1, epd.white)    
        else:
            for c in range(1,40,2):
                epd.image4Gray.fill_rect(10*c,10*r,10,10,epd.black)
            epd.image4Gray.text(str(r%10),1, 10*r+1, epd.black)                
    
    #epd.image4Gray.text('GRAY4 with white background',155, 111, epd.black)    
    epd.EPD_4IN2_4GrayDisplay(epd.buffer_4Gray)
    epd.Sleep()
            
    

