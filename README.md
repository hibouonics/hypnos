# Hibouonics Hypnos Firmware

Embedded firmware and hardware-interface code for **Hypnos**, a Hibouonics
low-power controller built around a Raspberry Pi Pico/Pico W and an MCP7940N
real-time clock (RTC).

The core driver schedules RTC alarms, reads power-fail information, exposes
battery-backed SRAM, and controls a `DONE` signal used by the external power
management hardware. A typical application wakes, performs its work, schedules
the next alarm, and asserts DONE to request that the controller remove power.

Start with the [user manual](docs/USER_MANUAL.md) for commissioning, examples,
the complete public API, troubleshooting, and known driver limitations.

> **Project status:** hardware firmware / active development. Validate changes
> on real hardware before relying on them in a deployed device.

## Features

- Read and set MCP7940N RTC time
- Schedule relative wake alarms
- Enable/disable and clear RTC alarm interrupts
- Control the external Hypnos `DONE` signal
- Read power-fail timestamps
- Access 64 bytes of battery-backed RTC SRAM
- Raspberry Pi Pico / Pico W compatible MicroPython code
- Host-side tests for hardware-independent date/time logic

## Repository layout

```text
hypnos/
├── firmware/
│   ├── hypnos.py          # Main Hibouonics Hypnos driver
│   └── main.py            # Minimal device entry point
├── drivers/
│   ├── epaper_4in2.py     # Waveshare e-paper driver
│   ├── oled_1inch3.py     # 1.3-inch OLED driver
│   └── pms5003.py         # PMS5003 particulate sensor driver
├── examples/
│   ├── basic_sleep.py
│   └── read_status.py
├── legacy/                # Selected earlier prototypes; not production code
├── tests/                 # Host-side unit tests
├── docs/
│   ├── HARDWARE.md
│   ├── USER_MANUAL.md
│   └── DEVELOPMENT.md
└── THIRD_PARTY_NOTICES.md
```

## Hardware

The active Hypnos firmware currently assumes:

| Signal | Connection | Purpose |
| --- | ---: | --- |
| SDA | GPIO 20 | I2C data to RTC |
| SCL | GPIO 21 | I2C clock to RTC |
| DONE | GPIO 22 | Power-management completion signal |
| RTC | I2C `0x6F` | MCP7940N real-time clock |

Use the GPIO numbers above, not physical header pin numbers. The constructor
accepts an I2C object and a DONE output pin; the defaults come from the example
scripts. See [hardware notes](docs/HARDWARE.md) before changing wiring.

## Getting started

### 1. Install MicroPython

Flash a current MicroPython build for your Raspberry Pi Pico or Pico W using the
normal MicroPython/Raspberry Pi workflow.

### 2. Copy the driver and inspect the RTC

Copy the active driver to the Pico filesystem using your MicroPython file
transfer tool:

```text
firmware/hypnos.py  -> /hypnos.py
```

The core firmware needs no files from `drivers/`. Run this at the MicroPython
REPL with the board powered:

```python
from machine import I2C, Pin
from hypnos import Hypnos


i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=100_000)
done = Pin(22, Pin.OUT, value=0)
if Hypnos.ADDRESS not in i2c.scan():
    raise RuntimeError("MCP7940N not found at 0x6F")

hypnos = Hypnos(i2c, done)
# Inspect saved power-fail data before start() or setting the clock.
hypnos.print_status()
```

Follow the manual's [first-time setup](docs/USER_MANUAL.md#first-time-setup)
to initialize an unset clock and verify oscillator and alarm-output settings.
The driver uses 24-hour time and weekdays Monday=0 through Sunday=6.

### 3. Schedule a wake-up

After commissioning, capture any saved power-fail data, call `hypnos.start()`,
and confirm `hypnos.oscillator_running()` before scheduling:

```python
# Finish and save application work before this call.
# Duration order: months, days, hours, minutes, seconds.
hypnos.sleep((0, 0, 0, 10, 0))  # request a wake-up in 10 minutes
```

`sleep()` programs alarm 0 and drives DONE high. It does not block Python or
call MicroPython's deep-sleep API; actual power removal and restoration depend
on the Hypnos hardware. Code after this call may never run.

Once the setup works, adapt `firmware/main.py` and copy it to `/main.py` for
automatic operation. The supplied script starts the oscillator, prints status,
and requests power-down with a five-second alarm on each boot. It assumes a
valid RTC time and compatible output configuration. If power-fail history
matters, move its status capture before `start()` as shown in the manual.

## Current driver limitations

The [review notes](docs/USER_MANUAL.md#current-driver-limitations) document
non-atomic clock reads/writes, incomplete input validation, a year-mask bug
affecting 2080-2099, and retained alarm-output configuration. Read these before
deploying unattended power cycling. This documentation update does not change
the firmware implementation.

## Development

The active driver intentionally avoids CPython-only dependencies so it remains
MicroPython-friendly. Hardware-independent logic can be checked on a desktop:

```bash
python -m unittest discover -s tests -v
```

For hardware validation, see [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md).

## Security and credentials

**Never commit Wi-Fi passwords, API tokens, private keys, or device-specific
credentials.** The original development archive contained local credentials;
they have intentionally been excluded from this cleaned repository. If those
values were ever committed to another repository, rotate them rather than only
deleting the file from the latest commit.

See [`SECURITY.md`](SECURITY.md) for disclosure guidance.

## Legacy code

`legacy/` contains selected development scripts for engineering reference. They
are not guaranteed to match the current module names, pinout, or API and should
not be treated as production firmware. Large upstream SDKs, nested Git
repositories, generated build files, duplicate vendor examples, and credential-
bearing experiments from the source archive are intentionally not included.

The redundant `drivers/mcp7940.py` helper has been removed. Historical scripts
`legacy/debug_i2c.py` and `legacy/hypnos_seed.py` still refer to its old
`MCP7940` module name; they are archival examples and are not runnable as
provided. Use `firmware/hypnos.py` for current RTC applications.

## Licensing

Hibouonics-owned code in this repository is available under the
[MIT License](LICENSE).
Third-party driver code remains under its original terms. Review
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) before making the repository
public.
