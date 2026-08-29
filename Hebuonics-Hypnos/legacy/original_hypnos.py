class Hypnos:
    def __init__(self, i2c, done):
        self._i2c = i2c
        self.done = done
    
    ADDRESS = 0x6f
    CENTURY = 2000
    ADDR_MEM = 0x20
    
    def sleep(self, t):
        if t == 0:
            self.disable_alarm()
            self.clear_alarm_iflag()
            self.set_done()
        elif t == 1:
            self.disable_alarm()
            self.clear_alarm_iflag()
            self.set_alarm_mask()
            self.enable_alarm()
            self.set_done()
        elif len(t)==5:
            self.disable_alarm()
            self.clear_alarm_iflag()
            self.set_alarm_mask()
#             alarm = self._add_time(self.time, t)
#             print(alarm)
#             print(alarm[-6:])
#             self.alarm = alarm
            self.alarm = self._add_time(self.time, t)[-6:]
            self.enable_alarm()
            print(self.alarm)
            self.set_done()
        else:
            print("error")
    
    @property
    def time(self):
        return ( # year, month, day, hour, minute, second, wkday
            self.CENTURY + self._bcd_to_decimal(self._read_bits(0x6, 0, 0x7f)),
            self._bcd_to_decimal(self._read_bits(0x5, 0, 0x1f)),
            self._bcd_to_decimal(self._read_bits(0x4, 0, 0x3f)),
            self._bcd_to_decimal(self._read_bits(0x2, 0, 0x3f)),
            self._bcd_to_decimal(self._read_bits(0x1, 0, 0x7f)),
            self._bcd_to_decimal(self._read_bits(0x0, 0, 0x7f)),
            # return the day of the week like utime.localtime()
            self._bcd_to_decimal(self._read_bits(0x3, 0, 0x07)-1),
            )
    
    @time.setter
    def time(self, settime):
        # year, month, day, hour, minute, second, wkday
        self._write_bits(0x6, 0, 0x7f, self._decimal_to_bcd(settime[0]-self.CENTURY))
        self._write_bits(0x5, 0, 0x1f, self._decimal_to_bcd(settime[1]))
        self._write_bits(0x4, 0, 0x3f, self._decimal_to_bcd(settime[2]))
        self._write_bits(0x2, 0, 0x3f, self._decimal_to_bcd(settime[3]))
        self._write_bits(0x1, 0, 0x7f, self._decimal_to_bcd(settime[4]))
        self._write_bits(0x0, 0, 0x7f, self._decimal_to_bcd(settime[5]))
        # add 1 to the day of the week from utime.localtime() for storage
        self._write_bits(0x3, 0, 0x07, self._decimal_to_bcd(settime[6]+1))        
            
    @property
    def alarm(self):
        return ( # month, day, hour, minute, second, wkday
            self._bcd_to_decimal(self._read_bits(0xf, 0, 0x1f)),
            self._bcd_to_decimal(self._read_bits(0xe, 0, 0x3f)),
            self._bcd_to_decimal(self._read_bits(0xc, 0, 0x3f)),
            self._bcd_to_decimal(self._read_bits(0xb, 0, 0x7f)),
            self._bcd_to_decimal(self._read_bits(0xa, 0, 0x7f)),
            # return the day of the week like utime.localtime()
            self._bcd_to_decimal(self._read_bits(0xd, 0, 0x07)-1),
            )
    
    @alarm.setter
    def alarm(self, settime):
        # month, day, hour, minute, second, wkday
        self._write_bits(0xf, 0, 0x1f, self._decimal_to_bcd(settime[0]))
        self._write_bits(0xe, 0, 0x3f, self._decimal_to_bcd(settime[1]))
        self._write_bits(0xc, 0, 0x3f, self._decimal_to_bcd(settime[2]))
        self._write_bits(0xb, 0, 0x7f, self._decimal_to_bcd(settime[3]))
        self._write_bits(0xa, 0, 0x7f, self._decimal_to_bcd(settime[4]))
        # add 1 to the day of the week from utime.localtime() for storage
        self._write_bits(0xd, 0, 0x07, self._decimal_to_bcd(settime[5]+1))        
        
    def start(self):
        # enable the oscillator
        self._write_bits(0x0, 7, 0x1, 1)
        # enable the battery backup
        self._write_bits(0x3, 3, 0x1, 1)
        
    def enable_alarm(self):
        self._write_bits(0x7, 4, 0xf, 9)

    def disable_alarm(self):
        self._write_bits(0x7, 4, 0x1, 0)

    def read_alarm_enable(self):
        return self._read_bits(0x7, 4, 0x1)
    
    def set_alarm_mask(self):
        self._write_bits(0xd, 4, 0x7, 7)

    def read_alarm_iflag(self):
        return self._read_bits(0xd, 3, 0x1)

    def clear_alarm_iflag(self):
        return self._write_bits(0xd, 3, 0x1, 0)
    
    def read_osc_enable(self):
        return self._read_bits(0x0, 7, 0x1)

    def read_osc_status(self):
        return self._read_bits(0x3, 5, 0x1)
    
    def read_pwrfail(self):
        return self._read_bits(0x3, 4, 0x1)

    @property
    def pwrdntime(self):
        wkday = self._bcd_to_decimal(self._read_bits(0x1b, 5, 0x07))
        if wkday != 0:
            wkday += -1
        return ( # month, day, hour, minute, 0, wkday
            self._bcd_to_decimal(self._read_bits(0x1b, 0, 0x1f)),
            self._bcd_to_decimal(self._read_bits(0x1a, 0, 0x3f)),
            self._bcd_to_decimal(self._read_bits(0x19, 0, 0x3f)),
            self._bcd_to_decimal(self._read_bits(0x18, 0, 0x7f)),
            0, # no second information for the power-fail time-stamp
            # return the day of the week like utime.localtime()
            wkday,
            )

    @property
    def pwruptime(self):
        wkday = self._bcd_to_decimal(self._read_bits(0x1f, 5, 0x07))
        if wkday != 0:
            wkday += -1
        return ( # month, day, hour, minute, 0, wkday
            self._bcd_to_decimal(self._read_bits(0x1f, 0, 0x1f)),
            self._bcd_to_decimal(self._read_bits(0x1e, 0, 0x3f)),
            self._bcd_to_decimal(self._read_bits(0x1d, 0, 0x3f)),
            self._bcd_to_decimal(self._read_bits(0x1c, 0, 0x7f)),
            0, # no second information for the power-fail time-stamp
            # return the day of the week like utime.localtime()
            wkday,
            )

    def clear_pwrfail(self):
        self._write_bits(0x3, 4, 0x1, 0)

    def clear_done(self):
        self.done.low()
        
    def set_done(self):
        self.done.high()

    def set_mem(self, addr, data):
        # set user memory: there is 64-byte of Battery-Backed SRAM.
        self._i2c.writeto_mem(self.ADDRESS, self.ADDR_MEM+addr, bytes([data]))       
        
    def get_mem(self, addr, nbytes):
        # read user memory: there is 64-byte of Battery-Backed SRAM.
        return self._i2c.readfrom_mem(self.ADDRESS, self.ADDR_MEM+addr, nbytes)
    
    @property
    def status(self):
        print(f"          time: {self.time}")
        print(f"        osc en: {self.read_osc_enable()}")
        print(f"    osc status: {self.read_osc_status()}")
        pwrfail = self.read_pwrfail()
        print(f"    power fail: {pwrfail}")
        if pwrfail == 1:
            print(f"                pwrdn fail at: {self.pwrdntime}")
            print(f"                pwrup fail at: {self.pwruptime}")
        print(f"  alarm enable: {self.read_alarm_enable()}")
        print(f"alarm int flag: {self.read_alarm_iflag()}")
        print(f"         alarm: {self.alarm}")
        
    @property
    def dump(self):
        return self._i2c.readfrom_mem(self.ADDRESS, 0, 32)

    def _decimal_to_bcd(self, decimal_value):
        # Converts a decimal value (0-99) to its BCD (Binary-Coded Decimal) representation.
        # 
        # Parameters:
        # - decimal_value: An integer between 0 and 99.
        # 
        # Returns:
        # - A BCD representation as an integer.

        if not (0 <= decimal_value <= 99):
            raise ValueError("Value must be between 0 and 99.")
        
        tens = decimal_value // 10
        ones = decimal_value % 10
        
        bcd_value = (tens << 4) | ones
        return bcd_value

    def _bcd_to_decimal(self, bcd_value):
        # Converts a BCD (Binary-Coded Decimal) value to its decimal representation.
        # 
        # Parameters:
        # - bcd_value: A BCD value (typically 8 bits) where the upper nibble represents tens 
        #              and the lower nibble represents ones.
        # 
        # Returns:
        # - A decimal representation as an integer.

        tens = (bcd_value >> 4) & 0x0F
        ones = bcd_value & 0x0F
        
        decimal_value = (tens * 10) + ones
        return decimal_value
    
    def _read_bits(self, register, start_bit, mask):
        # Read multiple bits from a register. The bits to read are specified by
        # the start_bit and mask.
        # 
        # Parameters:
        # - register: The register address to read from.
        # - start_bit: The position of the first bit to read.
        # - mask: The mask that determines which bits to read.
        # 
        # Returns:
        # The value of the specified bits, right-aligned to bit position 0.

        register_val = self._i2c.readfrom_mem(self.ADDRESS, register, 1)
        # Shift the masked bits to the rightmost position
        return (register_val[0] & (mask << start_bit)) >> start_bit

    def _write_bits(self, register, start_bit, mask, value):
        # Write multiple bits to a register. The bits to write are specified by
        # the start_bit and mask. Only the bits within the mask are modified.
        # 
        # Parameters:
        # - register: The register address to write to.
        # - start_bit: The position of the first bit to modify.
        # - mask: The mask that determines which bits to modify.
        # - value: The value to write to the masked bits.

        current = self._i2c.readfrom_mem(self.ADDRESS, register, 1)
        # Shift the mask and value to the correct bit positions
        shifted_mask = mask << start_bit
        shifted_value = (value << start_bit) & shifted_mask
        # Clear the bits specified by the mask in the current register value
        updated = (current[0] & ~shifted_mask) | shifted_value
        self._i2c.writeto_mem(self.ADDRESS, register, bytes([updated]))

    def _wkday(self, year, month, day):
        # Calculate the day of the week using Zeller's Congruence.
        if month < 3:
            month += 12
            year -= 1

        K = year % 100
        J = year // 100

        # Zeller's Congruence formula
        f = day + ((13 * (month + 1)) // 5) + K + (K // 4) + (J // 4) - 2 * J
        day_of_week = (f % 7) # 1 = Sunday, ..., 0 = Saturday

        # Mapping Zeller's output to 6 = Sunday, 0 = Monday, ..., 5 = Saturday
        day_of_week = (day_of_week + 5) % 7 
        
        return day_of_week

    def _is_leap_year(self, year):
        # Check if the given year is a leap year.
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    def _days_in_month(self, year, month):
        # Return the number of days in the given month of the given year.
        if month in {1, 3, 5, 7, 8, 10, 12}:
            return 31
        elif month in {4, 6, 9, 11}:
            return 30
        elif month == 2:
            return 29 if self._is_leap_year(year) else 28

    def _add_time(self, t, delta):
        year, month, day, hour, minute, second = t[:6]
        delta_months, delta_days, delta_hours, delta_minutes, delta_seconds = delta

        # Add seconds and handle overflow
        second += delta_seconds
        minute += second // 60
        second %= 60

        # Add minutes and handle overflow
        minute += delta_minutes
        hour += minute // 60
        minute %= 60

        # Add hours and handle overflow
        hour += delta_hours
        day += hour // 24
        hour %= 24

        # Add days and handle month overflow
        day += delta_days
        while True:
            days_in_current_month = self._days_in_month(year, month)
            if day <= days_in_current_month:
                break
            day -= days_in_current_month
            month += 1
            if month > 12:
                month = 1
                year += 1

        # Add months and handle year overflow
        month += delta_months
        while month > 12:
            month -= 12
            year += 1

        # Handle edge cases with day adjustment (e.g., end of month, leap year)
        while day > self._days_in_month(year, month):
            day -= self._days_in_month(year, month)
            month += 1
            if month > 12:
                month = 1
                year += 1

        return (year, month, day, hour, minute, second, self._wkday(year, month, day))


