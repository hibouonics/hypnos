from machine import Pin,SPI
import framebuf
from ePaper_4IN2 import EPD_4in2
from writer import Writer
import freesans20  # Font to use


    
# setup the display
epd = EPD_4in2()
x_offset = 8
y_offset = 5
text_size = 3

# clear the display buffers
epd.image1Gray.fill(0xff)
epd.image4Gray.fill(0xff)

epd.image4Gray.height = 300
epd.image4Gray.width = 400


# Instantiate a writer for a specific font
wri = Writer(epd.image4Gray, freesans20, epd.black, epd.white)  # verbose = False to suppress console output
Writer.set_textpos(epd, 0, 0)  # In case a previous test has altered this
wri.printstring('Sunday\n12 Aug 2018\n10.30am')

     

#epd.image4Gray.text('GRAY4 with white background',155, 111, epd.black)    
epd.EPD_4IN2_4GrayDisplay(epd.buffer_4Gray)
#epd.Sleep()
        



