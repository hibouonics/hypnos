"""Hibouonics Hypnos RTC and low-power control driver.

This module provides a small MicroPython-friendly interface to the MCP7940N
real-time clock used by the Hypnos hardware. It manages RTC time, alarm setup,
power-fail timestamps, battery-backed SRAM, and the external DONE signal used
to hand control back to the power-management circuit.
"""


class Hypnos:
    """Control the Hypnos RTC/power-management interface over I2C."""

    ADDRESS = 0x6F
    CENTURY = 2000
    SRAM_START = 0x20
    SRAM_SIZE = 64

    def __init__(self, i2c, done_pin):
        """Create a Hypnos controller.

        Args:
            i2c: MicroPython-compatible I2C object.
            done_pin: Output pin connected to the Hypnos DONE input.
        """
        self._i2c = i2c
        self.done_pin = done_pin

    def sleep(self, duration):
        """Request power-down, optionally scheduling a wake alarm.

        ``duration`` accepts:
        - ``0``: disable the alarm and assert DONE.
        - ``1``: enable the existing alarm configuration and assert DONE.
        - a 5-item tuple ``(months, days, hours, minutes, seconds)``: schedule
          an alarm relative to the current RTC time, then assert DONE.
        """
        if duration == 0:
            self.disable_alarm()
            self.clear_alarm_flag()
            self.set_done()
            return

        if duration == 1:
            self.disable_alarm()
            self.clear_alarm_flag()
            self.set_alarm_mask()
            self.enable_alarm()
            self.set_done()
            return

        if not isinstance(duration, (tuple, list)) or len(duration) != 5:
            raise ValueError(
                "duration must be 0, 1, or a 5-item "
                "(months, days, hours, minutes, seconds) sequence"
            )

        self.disable_alarm()
        self.clear_alarm_flag()
        self.set_alarm_mask()
        self.alarm = self._add_time(self.time, duration)[1:]
        self.enable_alarm()
        self.set_done()

    @property
    def time(self):
        """RTC time as ``(year, month, day, hour, minute, second, weekday)``."""
        return (
            self.CENTURY + self._bcd_to_decimal(self._read_bits(0x06, 0, 0x7F)),
            self._bcd_to_decimal(self._read_bits(0x05, 0, 0x1F)),
            self._bcd_to_decimal(self._read_bits(0x04, 0, 0x3F)),
            self._bcd_to_decimal(self._read_bits(0x02, 0, 0x3F)),
            self._bcd_to_decimal(self._read_bits(0x01, 0, 0x7F)),
            self._bcd_to_decimal(self._read_bits(0x00, 0, 0x7F)),
            self._bcd_to_decimal(self._read_bits(0x03, 0, 0x07)) - 1,
        )

    @time.setter
    def time(self, value):
        if len(value) < 7:
            raise ValueError("time must contain year, month, day, hour, minute, second, weekday")

        year, month, day, hour, minute, second, weekday = value[:7]
        self._write_bits(0x06, 0, 0x7F, self._decimal_to_bcd(year - self.CENTURY))
        self._write_bits(0x05, 0, 0x1F, self._decimal_to_bcd(month))
        self._write_bits(0x04, 0, 0x3F, self._decimal_to_bcd(day))
        self._write_bits(0x02, 0, 0x3F, self._decimal_to_bcd(hour))
        self._write_bits(0x01, 0, 0x7F, self._decimal_to_bcd(minute))
        self._write_bits(0x00, 0, 0x7F, self._decimal_to_bcd(second))
        self._write_bits(0x03, 0, 0x07, self._decimal_to_bcd(weekday + 1))

    @property
    def alarm(self):
        """Alarm as ``(month, day, hour, minute, second, weekday)``."""
        return (
            self._bcd_to_decimal(self._read_bits(0x0F, 0, 0x1F)),
            self._bcd_to_decimal(self._read_bits(0x0E, 0, 0x3F)),
            self._bcd_to_decimal(self._read_bits(0x0C, 0, 0x3F)),
            self._bcd_to_decimal(self._read_bits(0x0B, 0, 0x7F)),
            self._bcd_to_decimal(self._read_bits(0x0A, 0, 0x7F)),
            self._bcd_to_decimal(self._read_bits(0x0D, 0, 0x07)) - 1,
        )

    @alarm.setter
    def alarm(self, value):
        if len(value) != 6:
            raise ValueError("alarm must contain month, day, hour, minute, second, weekday")

        month, day, hour, minute, second, weekday = value
        self._write_bits(0x0F, 0, 0x1F, self._decimal_to_bcd(month))
        self._write_bits(0x0E, 0, 0x3F, self._decimal_to_bcd(day))
        self._write_bits(0x0C, 0, 0x3F, self._decimal_to_bcd(hour))
        self._write_bits(0x0B, 0, 0x7F, self._decimal_to_bcd(minute))
        self._write_bits(0x0A, 0, 0x7F, self._decimal_to_bcd(second))
        self._write_bits(0x0D, 0, 0x07, self._decimal_to_bcd(weekday + 1))

    def start(self):
        """Start the RTC oscillator and enable battery backup."""
        self._write_bits(0x00, 7, 0x01, 1)
        self._write_bits(0x03, 3, 0x01, 1)

    def enable_alarm(self):
        """Enable alarm 0 interrupt output without changing unrelated bits."""
        self._write_bits(0x07, 4, 0x01, 1)

    def disable_alarm(self):
        """Disable alarm 0 interrupt output."""
        self._write_bits(0x07, 4, 0x01, 0)

    def alarm_enabled(self):
        return bool(self._read_bits(0x07, 4, 0x01))

    def set_alarm_mask(self, mask=0x07):
        """Set the MCP7940 alarm match mask (default: match all fields)."""
        if not 0 <= mask <= 0x07:
            raise ValueError("alarm mask must be between 0 and 7")
        self._write_bits(0x0D, 4, 0x07, mask)

    def alarm_flag(self):
        return bool(self._read_bits(0x0D, 3, 0x01))

    def clear_alarm_flag(self):
        self._write_bits(0x0D, 3, 0x01, 0)

    # Backward-compatible aliases used by earlier Hibouonics scripts.
    read_alarm_enable = alarm_enabled
    read_alarm_iflag = alarm_flag
    clear_alarm_iflag = clear_alarm_flag

    def oscillator_enabled(self):
        return bool(self._read_bits(0x00, 7, 0x01))

    def oscillator_running(self):
        return bool(self._read_bits(0x03, 5, 0x01))

    def power_failed(self):
        return bool(self._read_bits(0x03, 4, 0x01))

    read_osc_enable = oscillator_enabled
    read_osc_status = oscillator_running
    read_pwrfail = power_failed

    @property
    def power_down_time(self):
        return self._read_power_timestamp(0x18)

    @property
    def power_up_time(self):
        return self._read_power_timestamp(0x1C)

    # Backward-compatible property names.
    pwrdntime = power_down_time
    pwruptime = power_up_time

    def _read_power_timestamp(self, start_register):
        minute_reg = start_register
        hour_reg = start_register + 1
        day_reg = start_register + 2
        month_reg = start_register + 3
        raw_weekday = self._bcd_to_decimal(self._read_bits(month_reg, 5, 0x07))
        weekday = raw_weekday - 1 if raw_weekday else 0
        return (
            self._bcd_to_decimal(self._read_bits(month_reg, 0, 0x1F)),
            self._bcd_to_decimal(self._read_bits(day_reg, 0, 0x3F)),
            self._bcd_to_decimal(self._read_bits(hour_reg, 0, 0x3F)),
            self._bcd_to_decimal(self._read_bits(minute_reg, 0, 0x7F)),
            0,
            weekday,
        )

    def clear_power_fail(self):
        self._write_bits(0x03, 4, 0x01, 0)

    clear_pwrfail = clear_power_fail

    def clear_done(self):
        """Deassert the external DONE signal."""
        if hasattr(self.done_pin, "low"):
            self.done_pin.low()
        else:
            self.done_pin.value(0)

    def set_done(self):
        """Assert the external DONE signal."""
        if hasattr(self.done_pin, "high"):
            self.done_pin.high()
        else:
            self.done_pin.value(1)

    def set_memory(self, address, data):
        """Write one byte to the RTC's 64-byte battery-backed SRAM."""
        if not 0 <= address < self.SRAM_SIZE:
            raise ValueError("SRAM address must be between 0 and 63")
        if not 0 <= data <= 0xFF:
            raise ValueError("data must fit in one byte")
        self._i2c.writeto_mem(self.ADDRESS, self.SRAM_START + address, bytes([data]))

    def get_memory(self, address, length=1):
        """Read bytes from the RTC's battery-backed SRAM."""
        if address < 0 or length < 0 or address + length > self.SRAM_SIZE:
            raise ValueError("requested SRAM range must stay within 0..63")
        return self._i2c.readfrom_mem(self.ADDRESS, self.SRAM_START + address, length)

    set_mem = set_memory
    get_mem = get_memory

    def status(self):
        """Return a machine-readable snapshot of RTC and alarm state."""
        result = {
            "time": self.time,
            "oscillator_enabled": self.oscillator_enabled(),
            "oscillator_running": self.oscillator_running(),
            "power_failed": self.power_failed(),
            "alarm_enabled": self.alarm_enabled(),
            "alarm_flag": self.alarm_flag(),
            "alarm": self.alarm,
        }
        if result["power_failed"]:
            result["power_down_time"] = self.power_down_time
            result["power_up_time"] = self.power_up_time
        return result

    def print_status(self):
        """Print a readable status report for serial debugging."""
        for key, value in self.status().items():
            print("{}: {}".format(key, value))

    @property
    def dump(self):
        """Return the first 32 RTC registers as bytes."""
        return self._i2c.readfrom_mem(self.ADDRESS, 0, 32)

    @staticmethod
    def _decimal_to_bcd(value):
        if not 0 <= value <= 99:
            raise ValueError("BCD value must be between 0 and 99")
        return ((value // 10) << 4) | (value % 10)

    @staticmethod
    def _bcd_to_decimal(value):
        return (((value >> 4) & 0x0F) * 10) + (value & 0x0F)

    def _read_bits(self, register, start_bit, mask):
        register_value = self._i2c.readfrom_mem(self.ADDRESS, register, 1)[0]
        return (register_value >> start_bit) & mask

    def _write_bits(self, register, start_bit, mask, value):
        if value & ~mask:
            raise ValueError("value does not fit inside the supplied bit mask")
        current = self._i2c.readfrom_mem(self.ADDRESS, register, 1)[0]
        shifted_mask = mask << start_bit
        updated = (current & ~shifted_mask) | ((value & mask) << start_bit)
        self._i2c.writeto_mem(self.ADDRESS, register, bytes([updated]))

    @staticmethod
    def _weekday(year, month, day):
        """Return weekday using MicroPython's convention: Monday=0..Sunday=6."""
        if month < 3:
            month += 12
            year -= 1
        k = year % 100
        j = year // 100
        zeller = (day + (13 * (month + 1)) // 5 + k + k // 4 + j // 4 - 2 * j) % 7
        return (zeller + 5) % 7

    @staticmethod
    def _is_leap_year(year):
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    @classmethod
    def _days_in_month(cls, year, month):
        if month in (1, 3, 5, 7, 8, 10, 12):
            return 31
        if month in (4, 6, 9, 11):
            return 30
        if month == 2:
            return 29 if cls._is_leap_year(year) else 28
        raise ValueError("month must be between 1 and 12")

    @classmethod
    def _add_time(cls, current, delta):
        """Add ``(months, days, hours, minutes, seconds)`` to an RTC tuple."""
        year, month, day, hour, minute, second = current[:6]
        add_months, add_days, add_hours, add_minutes, add_seconds = delta

        if min(delta) < 0:
            raise ValueError("negative sleep durations are not supported")

        # Apply months first and clamp the day to the resulting month.
        total_months = (year * 12 + (month - 1)) + add_months
        year, month_index = divmod(total_months, 12)
        month = month_index + 1
        day = min(day, cls._days_in_month(year, month))

        second += add_seconds
        minute += add_minutes + second // 60
        second %= 60
        hour += add_hours + minute // 60
        minute %= 60
        day += add_days + hour // 24
        hour %= 24

        while day > cls._days_in_month(year, month):
            day -= cls._days_in_month(year, month)
            month += 1
            if month > 12:
                month = 1
                year += 1

        return (year, month, day, hour, minute, second, cls._weekday(year, month, day))
