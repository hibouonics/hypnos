# Hardware Notes

## Core interface

The current firmware is written for a Raspberry Pi Pico/Pico W using I2C bus 0.
The MCP7940N RTC is expected at 7-bit address `0x6F`.

| Function | GPIO | Notes |
| --- | ---: | --- |
| I2C SDA | 20 | Pull-up enabled in firmware; board-level pull-ups may also exist |
| I2C SCL | 21 | Pull-up enabled in firmware; board-level pull-ups may also exist |
| DONE | 22 | Output to external Hypnos power-management logic |

## RTC behavior

The MCP7940N provides the RTC, alarm registers, power-fail timestamps, and 64
bytes of battery-backed SRAM used by the Hypnos driver.

Calling `Hypnos.start()` enables the oscillator and battery-backup bit. Calling
`Hypnos.sleep((months, days, hours, minutes, seconds))` programs a relative alarm
and then asserts DONE.

Capture power-fail records before calling `start()` or assigning the time;
these calls write the weekday register and can clear the records. Follow the
[user manual](USER_MANUAL.md) for first-time clock setup, alarm-output checks,
and the current driver's limitations.

## Optional reference drivers

Some examples may use these optional reference drivers for additional
peripherals:

| Peripheral | Reference driver |
| --- | --- |
| 1.3-inch OLED | [`oled_1inch3.py`](../drivers/oled_1inch3.py) |
| Waveshare 4.2-inch e-paper display | [`epaper_4in2.py`](../drivers/epaper_4in2.py) |
| PMS5003 particulate-matter sensor | [`pms5003.py`](../drivers/pms5003.py) |

The main driver, [`firmware/hypnos.py`](../firmware/hypnos.py), does not require
these files or peripherals. Copy an optional driver to the device only when
an example or your application uses it.

## Bring-up checklist

1. Confirm I2C wiring and logic voltage before powering the board.
2. Run an I2C scan and verify address `0x6F` appears.
3. Read the RTC time before writing it.
4. Verify GPIO 22 behavior with the power controller disconnected or in a safe
   test configuration.
5. Test a short alarm interval before using long sleep periods.
6. Validate power-fail timestamp and battery backup behavior on actual hardware.
