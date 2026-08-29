"""Minimal Hebuonics Hypnos firmware example for Raspberry Pi Pico/Pico W."""

from machine import I2C, Pin
from hypnos import Hypnos

I2C_ID = 0
SDA_PIN = 20
SCL_PIN = 21
DONE_PIN = 22


def main():
    i2c = I2C(I2C_ID, sda=Pin(SDA_PIN, Pin.PULL_UP), scl=Pin(SCL_PIN, Pin.PULL_UP))
    done = Pin(DONE_PIN, Pin.OUT)
    done.value(0)

    hypnos = Hypnos(i2c, done)
    hypnos.start()
    hypnos.print_status()

    # Example: wake again after 5 seconds, then signal the power controller.
    hypnos.sleep((0, 0, 0, 0, 5))


if __name__ == "__main__":
    main()
