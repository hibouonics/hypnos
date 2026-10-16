# Hypnos User Manual

The main Hypnos driver is [`firmware/hypnos.py`](../firmware/hypnos.py). It runs
on MicroPython on the Raspberry Pi Pico/Pico W and provides the `Hypnos` class
for the RTC, wake alarm, battery-backed memory, and DONE output.

Start with [first-time setup](#first-time-setup). You only need `hypnos.py` on
the Pico to use the core features. The files in `drivers/` are optional reference
drivers that some examples may use for extra peripherals.

The implementation was reviewed against Microchip's
[MCP7940N datasheet, DS20005010J](https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/MCP7940N-Battery-Backed-I2C-RTCC-with-SRAM-20005010J.pdf).
The API descriptions below follow the source code. The review notes identify
behavior that still needs firmware changes or hardware verification.

## Contents

- [Hardware and installation](#hardware-and-installation)
- [First-time setup](#first-time-setup)
- [Normal operation](#normal-operation)
- [Clock initialization](#clock-initialization)
- [Wake-output configuration](#wake-output-configuration)
- [Time and alarm formats](#time-and-alarm-formats)
- [Scheduling and DONE](#scheduling-and-done)
- [Power-fail records](#power-fail-records)
- [Battery-backed memory](#battery-backed-memory)
- [API reference](#api-reference)
- [Datasheet reference](#datasheet-reference)
- [Current driver limitations](#current-driver-limitations)
- [Troubleshooting and validation](#troubleshooting-and-validation)

## Hardware and installation

| Connection | Example configuration |
| --- | --- |
| Host | Raspberry Pi Pico/Pico W running MicroPython |
| I2C | Bus 0; SDA GPIO 20; SCL GPIO 21 |
| RTC address | `0x6F` (7-bit address; decimal 111 in a scan) |
| DONE | GPIO 22, output; initialize low |
| Wake path | RTC alarm output through the board's power-management circuit |

GPIO numbers are not physical header pin numbers. Verify the board's supply,
common ground, pull-ups, backup supply, and DONE/wake wiring using its schematic
and [hardware notes](HARDWARE.md). The chip datasheet does not specify the
Hypnos board's power-controller timing or wiring.

## First-time setup

### 1. Copy the main driver

Install MicroPython for your Pico/Pico W, then copy
[`firmware/hypnos.py`](../firmware/hypnos.py) to the device as `/hypnos.py` using
your usual MicroPython editor or file-transfer tool. No files from `drivers/`
are needed. Leave `/main.py` off the device until the manual test works.

### 2. Connect and read the clock

With the board powered, run this at the MicroPython REPL. These GPIO numbers
match the repository examples; check your board revision and use suitable
board-level I2C pull-ups.

```python
from machine import I2C, Pin
from hypnos import Hypnos

i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=100_000)
done = Pin(22, Pin.OUT, value=0)
if Hypnos.ADDRESS not in i2c.scan():
    raise RuntimeError("MCP7940N not found at 0x6F")

hypnos = Hypnos(i2c, done)
hypnos.print_status()
```

This reads the current state without requesting power-down. Save any reported
power-fail timestamps you need before calling `start()` or setting the time;
both operations can clear those records.

If the clock is unset or incorrect, follow [clock initialization](#clock-initialization)
once, then return here. Skip that procedure if the clock already has the correct
date, time, and weekday in 24-hour mode. Do not reset the clock on every boot.

### 3. Check the clock and try a wake-up

```python
import time

hypnos.start()
time.sleep(2)
if not hypnos.oscillator_running():
    raise RuntimeError("RTC not running; see Troubleshooting and validation")
print(hypnos.time)
time.sleep(2)
print(hypnos.time)  # confirm the clock advances
```

The two-second startup wait is a practical check, not a guaranteed hardware
startup time. If the check fails, inspect the oscillator and power supply before
continuing.

Before the first power-cycle test, complete the
[wake-output check](#wake-output-configuration) for your board. The current
driver retains those output settings. Then finish and save any work and run:

```python
hypnos.sleep((0, 0, 0, 1, 0))  # request a wake-up in one minute
```

`sleep()` raises DONE to request power removal; the external controller must
remove and restore power. USB or another supply may keep the Pico powered.
Observe the wake cycle before proceeding to [normal operation](#normal-operation)
and adding an automatic `/main.py`.

## Normal operation

A typical boot sequence is: hold DONE low, capture retained state, start/check
the RTC, do application work, save results, then request the next wake-up.
After commissioning, the following can form the body of your `/main.py`:

```python
from machine import I2C, Pin
from hypnos import Hypnos
import time

i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=100_000)
hypnos = Hypnos(i2c, Pin(22, Pin.OUT, value=0))

# Read before start(): save to your log/storage if it must survive power-off.
previous = hypnos.status()
print(previous)
hypnos.start()

deadline = time.ticks_add(time.ticks_ms(), 2000)
while not hypnos.oscillator_running():
    if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
        raise RuntimeError("RTC oscillator not running")
    time.sleep_ms(10)

# Perform measurements or other application work here; save/close files.
hypnos.sleep((0, 0, 0, 10, 0))
```

This assumes the time, weekday, 24-hour mode, and wake-output settings were
already verified. Holding a Python variable such as `previous` does not
preserve it after board power is removed.

`firmware/main.py` and `examples/basic_sleep.py` are minimal five-second
demos. Neither initializes the calendar or checks oscillator startup. Both
call `start()` before reporting state, so use the ordering above if you need
the previous power-fail record. `examples/read_status.py` only reads status.

## Clock initialization

Do this once during commissioning or when the RTC has lost valid time.
Do not overwrite a working clock with a fixed example date on every boot.

The current `time` setter does not stop the clock or select 24-hour mode.
The following commissioning example handles those steps for a board using
the normal crystal oscillator. It intentionally resets the clock after you
have saved any existing power-fail records. Replace the example tuple with
the current date, time, and correct weekday before running it.

```python
import time

# Continue with i2c and hypnos from first-time setup.
new_time = (2026, 9, 20, 12, 0, 0, 6)  # example only: Sunday at noon
address = Hypnos.ADDRESS
control = i2c.readfrom_mem(address, 0x07, 1)[0]
if control & 0x08:
    raise RuntimeError("External clock mode needs a board-specific setup")

hypnos.disable_alarm()
seconds = i2c.readfrom_mem(address, 0x00, 1)[0]
i2c.writeto_mem(address, 0x00, bytes([seconds & 0x7F]))  # clear ST
deadline = time.ticks_add(time.ticks_ms(), 1000)
while hypnos.oscillator_running():
    if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
        raise RuntimeError("RTC oscillator did not stop")
    time.sleep_ms(10)

i2c.writeto_mem(address, 0x02, b"\x00")  # select 24-hour mode
i2c.writeto_mem(address, 0x06, b"\x00")  # clear retained year bit 7
hypnos.time = new_time
hypnos.clear_alarm_flag()
hypnos.start()

deadline = time.ticks_add(time.ticks_ms(), 2000)
while not hypnos.oscillator_running():
    if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
        raise RuntimeError("RTC oscillator did not start; inspect hardware")
    time.sleep_ms(10)
print(hypnos.time)
```

The timeouts above are application choices, not guaranteed oscillator startup
times. With the current year-mask bug, use years 2000-2079 and validate the
entire tuple before writing. A failed write can leave a partially set clock;
repeat commissioning with valid input before scheduling an alarm.

Choose a time convention for your application, preferably UTC, and keep it
consistent. The driver performs no time-zone conversion, network time sync,
or daylight-saving adjustment.

## Wake-output configuration

Before testing power cycling, inspect the current register values:

```python
control = i2c.readfrom_mem(Hypnos.ADDRESS, 0x07, 1)[0]
alarm_weekday = i2c.readfrom_mem(Hypnos.ADDRESS, 0x0D, 1)[0]
print("CONTROL:", hex(control))
print("ALM0WKDAY:", hex(alarm_weekday))
```

For the alarm-0-only application described here, verify SQWEN (CONTROL bit 6)
and ALM1EN (bit 5) are clear. Verify ALMPOL (ALM0WKDAY bit 7) against the
power-controller input: zero selects an asserted-low signal, one an
asserted-high signal. See the [datasheet reference](#datasheet-reference).
The public driver does not configure these bits; retained settings from earlier firmware need
board-specific correction before use. Do not assume `start()` resets them.

## Time and alarm formats

Pass integers in these exact orders:

| Value | Format | Notes |
| --- | --- | --- |
| `hypnos.time` | `(year, month, day, hour, minute, second, weekday)` | Read/write; 24-hour format expected |
| `hypnos.alarm` | `(month, day, hour, minute, second, weekday)` | Read/write alarm 0; no year |
| Relative duration | `(months, days, hours, minutes, seconds)` | Nonnegative offsets; tuple or list |
| Power timestamp | `(month, day, hour, minute, 0, weekday)` | Read-only; seconds position is a placeholder |

Use months 1-12, valid calendar days, hours 0-23, minutes/seconds 0-59, and
weekdays Monday=0 through Sunday=6. The driver stores weekday plus one and
subtracts one when reading. Set the weekday to agree with the calendar date:
relative alarm calculation recomputes it and can disagree with an incorrectly
initialized RTC weekday.

The `time` setter accepts at least seven items and ignores extra items. The
`alarm` setter requires exactly six. Tuple length and BCD checks do not provide
complete calendar validation; for example, February 31 is not rejected.

## Scheduling and DONE

| Call | Current behavior |
| --- | --- |
| `sleep((0, 0, 0, 10, 0))` | Calculates an alarm ten minutes after the RTC read, enables alarm 0, then drives DONE high |
| `sleep(0)` | Disables alarm 0, clears its flag, then drives DONE high |
| `sleep(1)` | Clears the old flag, forces mask 7, enables the existing alarm-0 values, then drives DONE high |
| `clear_done()` | Drives DONE low |
| `set_done()` | Drives DONE high without programming an alarm |

`sleep(1)` does not mean one second. Use `(0, 0, 0, 0, 1)` for that offset,
though such a short interval may be missed during setup or power sequencing.
Use a comfortably longer interval for initial hardware testing. `sleep(0)`
does not establish a next alarm-0 wake event; ensure your system has the
intended way to power up again. It does not disable alarm 1 or other wake paths.

For relative durations, months are applied first and the day is clamped to the
destination month. January 31 plus one month becomes February 28 (29 in a leap
year); days and clock offsets are then added. Values such as 90 minutes carry
into hours. Negative offsets are rejected. Use a positive total duration:
an all-zero tuple programs the current time and still asserts DONE.

The target year is discarded when `sleep()` writes the alarm. Treat this as
calendar matching, not an arbitrary multi-year timer. A missed target can
leave the board waiting for a later matching date and weekday. Wake intervals
are calculated from the RTC read during `sleep()`, not from the instant that
power is physically removed.

### Program an alarm without powering down

After commissioning, set a future date with the correct weekday:

```python
hypnos.disable_alarm()
hypnos.set_alarm_mask()  # default 7
hypnos.alarm = (9, 21, 8, 30, 0, 0)  # example: Monday, September 21, 08:30
hypnos.clear_alarm_flag()
hypnos.enable_alarm()
print(hypnos.alarm, hypnos.alarm_enabled())
```

Replace the example target before running it. Assignment alone does not enable
the alarm, clear its flag, or assert DONE. To hand control to the power circuit
after this setup, call `hypnos.set_done()` as your final action.

For other match modes, use only the masks listed in the
[datasheet reference](#datasheet-reference). The current setter also accepts reserved values 5 and 6; avoid them. Calling
`sleep(1)` or `sleep(duration)` after selecting a custom mask overwrites that
mask with 7. To preserve a custom mask, explicitly configure/clear/enable the
alarm and then call `set_done()`.

DONE is an electrical request, not a Python delay. The method may return while
the controller is still switching power, or execution may stop before your
next statement. Complete file writes, communications, and logging beforehand.

## Power-fail records

Read `power_failed()` first. When true, capture both properties before any call
that writes RTCWKDAY:

```python
if hypnos.power_failed():
    down = hypnos.power_down_time
    up = hypnos.power_up_time
    print("Power down:", down)
    print("Power up:", up)
    # Save both records to your chosen storage before acknowledging them.
    hypnos.clear_power_fail()
```

The tuples contain no year, and their seconds value is always the driver's
placeholder `0`, not a measured second. A cleared timestamp may contain zero
month/day values; it is not a valid calendar date. Do not use these records
alone to infer a precise elapsed time across year boundaries.

`start()`, setting `time`, and `clear_power_fail()` all write RTCWKDAY in this
implementation. The datasheet rule above means each can erase the retained
record. A normal host fake that merely stores register bytes does not model
that side effect.

## Battery-backed memory

The API uses offsets 0-63; it adds `SRAM_START` internally. Do not pass raw
register addresses to these methods.

```python
hypnos.set_memory(0, 42)         # write one integer byte, 0-255
value = hypnos.get_memory(0)[0]  # reads return bytes, even for one byte
print(value)
print(hypnos.get_memory(0, 64))  # all 64 bytes
```

`set_memory()` writes one byte at a time. `get_memory(address, length)` must
stay within the memory region. The methods raise `ValueError` for out-of-range
requests. Use a version marker and integrity check for application state;
the driver supplies no initialization, allocation, checksum, or transactional
multi-byte update. Treat a missing or invalid marker as uninitialized data.

## API reference

All methods below are on a `Hypnos(i2c, done_pin)` instance. The I2C object must
provide `readfrom_mem` and `writeto_mem`. The pin must offer `low`/`high` or
`value(0)`/`value(1)`. Creating an instance only stores these objects; it does
not initialize the RTC or configure the alarm output.

| Member | Result or effect |
| --- | --- |
| `start()` | Sets oscillator-enable and battery-backup bits; does not wait for startup |
| `time` | Read/write seven-item clock tuple |
| `alarm` | Read/write six-item alarm-0 tuple |
| `sleep(duration)` | Configures alarm behavior and asserts DONE; see scheduling table |
| `enable_alarm()` / `disable_alarm()` | Set/clear alarm-0 enable only |
| `alarm_enabled()` | Boolean alarm-0 enable state |
| `set_alarm_mask(mask=0x07)` | Writes the alarm-0 comparison mask |
| `alarm_flag()` / `clear_alarm_flag()` | Read/clear the alarm-0 match flag |
| `oscillator_enabled()` | Boolean ST control bit |
| `oscillator_running()` | Boolean OSCRUN status bit |
| `power_failed()` | Boolean PWRFAIL flag |
| `power_down_time` / `power_up_time` | Read-only six-item timestamp tuples |
| `clear_power_fail()` | Acknowledges the retained power-fail event |
| `clear_done()` / `set_done()` | Drive the supplied DONE pin low/high |
| `set_memory(address, data)` | Write one byte at an SRAM offset |
| `get_memory(address, length=1)` | Return SRAM data as `bytes` |
| `status()` | Return a dictionary of time, oscillator, power-fail, and alarm state |
| `print_status()` | Print one status key/value per line |
| `dump` | Read-only property returning 32 register bytes from `0x00`; excludes SRAM |

`status()` always includes `time`, `oscillator_enabled`, `oscillator_running`,
`power_failed`, `alarm_enabled`, `alarm_flag`, and `alarm`. When `power_failed`
is true it also includes `power_down_time` and `power_up_time`. It performs
multiple I2C reads, so it is not one simultaneous hardware snapshot.

Compatibility aliases are retained:

| Old name | Current name |
| --- | --- |
| `read_alarm_enable` | `alarm_enabled` |
| `read_alarm_iflag` / `clear_alarm_iflag` | `alarm_flag` / `clear_alarm_flag` |
| `read_osc_enable` / `read_osc_status` | `oscillator_enabled` / `oscillator_running` |
| `read_pwrfail` / `clear_pwrfail` | `power_failed` / `clear_power_fail` |
| `pwrdntime` / `pwruptime` | `power_down_time` / `power_up_time` properties |
| `set_mem` / `get_mem` | `set_memory` / `get_memory` |

I2C exceptions propagate to the caller; there is no retry or automatic recovery.
An exception during a sequence can leave registers partly updated. Do not
assert DONE from a `finally` block after a failed alarm setup.

## Datasheet reference

The following summarizes the hardware rules relevant to this driver; see the
[datasheet](https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/MCP7940N-Battery-Backed-I2C-RTCC-with-SRAM-20005010J.pdf)
at the cited sections:

- Table 1-2 and sections 3-4: use up to 100 kHz below 2.5 V, or 400 kHz at
  2.5-5.5 V. SDA and open-drain MFP require pull-ups. I2C is unavailable on
  backup power.
- Section 5.3: read time in one transaction; stop the clock source and wait for
  OSCRUN to clear before setting time, then restart. RTCYEAR uses all eight bits.
- Register 5-4 and section 5.7.1: writing RTCWKDAY clears PWRFAIL and its
  timestamps; clearing it permits a new event to be recorded.
- Table 5-5: masks 0-4 match seconds, minutes, hours, weekday, or date,
  respectively; 5-6 are reserved; 7 matches all six alarm fields, including
  weekday. There is no alarm year. A still-matching condition can reassert a
  cleared flag.
- Section 5.5.2: alarm output requires SQWEN=0; polarity and alarm 1 also affect
  MFP. Alarm output works on backup power.
- Section 6: SRAM occupies `0x20-0x5F`, is not initialized at power-on, and
  needs a present, enabled backup supply for retention without VCC.

## Current driver limitations

These are findings from reviewing the current source against the datasheet
[reference](#datasheet-reference). They are not firmware fixes delivered by
this manual.

| Finding | User impact and recommended firmware improvement |
| --- | --- |
| `time` reads each field separately | A rollover can mix old and new fields and produce a wrong relative alarm. Read/decode the seven clock bytes in one transaction. |
| `time` writes while the oscillator may be running | Clock updates can race a tick. Implement stop/wait/write/restart and validate the entire tuple before changing registers. The clock-initialization procedure handles a crystal-based setup explicitly. |
| RTCYEAR is masked with `0x7F` | Writing 2080-2099 raises `ValueError`; reading stored `0x80` yields 2000. Use `0xFF` for the year register and explicitly define the supported century. A retained year bit 7 is also preserved by the current setter. |
| Hour handling assumes 24-hour mode | The getters decode 12-hour data incorrectly, and the setter preserves the mode bit. Select 24-hour mode deliberately or implement conversion. |
| `start()` writes RTCWKDAY before the bundled demos print status | Prior power-fail records can be lost. Capture them first and consider avoiding unnecessary register writes in initialization. |
| Alarm setup preserves SQWEN, ALM1EN, and ALMPOL | Previously configured modes can prevent the intended wake signal. Add an explicit board-aware alarm-output setup API. |
| `set_alarm_mask()` accepts 5 and 6 | Reject reserved masks, not just values outside 0-7. |
| Date, weekday, and duration validation is incomplete | Invalid values can reach registers; a negative duration is rejected only after alarm disable/flag/mask changes. Validate all arguments and the target before changing hardware. |
| No alarm-year field or missed-target check | Long offsets and setup delays are not guaranteed to produce the intended wake. Check the programmed target and supported scheduling horizon before asserting DONE. |

The class does not expose alarm 1, square-wave configuration, oscillator
calibration, or external-clock setup. It also cannot verify the external
power-controller circuit. Avoid treating these capabilities as configured
simply because the chip supports them.

## Troubleshooting and validation

| Symptom | Checks |
| --- | --- |
| `ImportError: hypnos` | Copy the active driver to `/hypnos.py` on the Pico, not only to the host computer. |
| I2C scan misses `0x6F` or an I2C `OSError` occurs | Check primary RTC power, ground, GPIO assignment, pull-ups, and bus frequency. I2C requires primary RTC power; it is unavailable on backup power alone. |
| Time is zero, invalid, or not advancing | Commission the calendar; compare `oscillator_enabled()` with `oscillator_running()` and inspect the crystal circuit. |
| Wrong hour/year | Check 24-hour mode and the year-mask limitation. |
| No power-fail record after boot | Capture it before `start()` or setting `time`; verify backup operation on hardware. |
| Alarm flag sets but the board never wakes | Check MFP pull-up, SQWEN, ALM1EN, polarity, and the external wake path. |
| Immediate wake or missed wake | Verify weekday, future target, flag state, retained output settings, and adequate interval for power switching. |
| DONE is high but the Pico stays on | Check controller wiring and whether USB or another supply keeps the Pico powered. |
| SRAM data is unexpected | Check your initialization marker, address offsets, and backup retention. |

Run the host tests from the repository root:

```bash
python -m unittest discover -s tests -v
```

The eight current tests cover BCD conversion, a clock tuple round trip, leap-day
and month-end arithmetic, SRAM bounds, control-bit preservation, and basic
sleep behavior/input rejection. Their fake I2C bus does not simulate ticking,
MFP logic, oscillator transitions, or power-fail register side effects.

On the actual board, verify time advances, perform a short alarm cycle with
enough time to observe it, and check both DONE and the RTC wake output. Test
retention and capture power-fail records before initialization writes. Exercise
midnight/month-end scheduling before unattended deployment. Record the PCB
revision, firmware version, supply arrangement, and observed timing.
