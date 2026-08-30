# Hibouonics Hypnos Firmware

Embedded firmware and hardware-interface code for **Hypnos**, a Hibouonics
low-power controller built around a Raspberry Pi Pico/Pico W and an MCP7940N
real-time clock (RTC).

The core driver schedules RTC alarms, records power-fail information, exposes
battery-backed SRAM, and controls a `DONE` signal used by the external power
management hardware. The repository also contains optional display and air-
quality drivers plus selected historical prototypes from development.

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
- Optional OLED, e-paper, and PMS5003 sensor drivers
- Host-side tests for hardware-independent date/time logic

## Repository layout

```text
Hibouonics-Hypnos/
├── firmware/
│   ├── hypnos.py          # Main Hibouonics Hypnos driver
│   └── main.py            # Minimal device entry point
├── drivers/
│   ├── epaper_4in2.py     # Waveshare e-paper driver
│   ├── mcp7940.py         # Legacy/reference MCP7940 helper
│   ├── oled_1inch3.py     # 1.3-inch OLED driver
│   └── pms5003.py         # PMS5003 particulate sensor driver
├── examples/
│   ├── basic_sleep.py
│   └── read_status.py
├── legacy/                # Selected earlier prototypes; not production code
├── tests/                 # Host-side unit tests
├── docs/
│   ├── HARDWARE.md
│   └── DEVELOPMENT.md
└── THIRD_PARTY_NOTICES.md
```

## Hardware

The active Hypnos firmware currently assumes:

| Signal | Pico GPIO | Purpose |
| --- | ---: | --- |
| SDA | GPIO 20 | I2C data to RTC |
| SCL | GPIO 21 | I2C clock to RTC |
| DONE | GPIO 22 | Power-management completion signal |
| RTC | I2C `0x6F` | MCP7940N real-time clock |

See [`docs/HARDWARE.md`](docs/HARDWARE.md) before changing wiring or pin
assignments.

## Getting started

### 1. Install MicroPython

Flash a current MicroPython build for your Raspberry Pi Pico or Pico W using the
normal MicroPython/Raspberry Pi workflow.

### 2. Copy the firmware

Copy these files to the Pico filesystem:

```text
firmware/hypnos.py  -> /hypnos.py
firmware/main.py    -> /main.py
```

Optional hardware features may also require files from `drivers/`.

### 3. Run

On boot, `main.py` creates the I2C bus, initializes Hypnos, prints its current
status, schedules a wake event five seconds in the future, and asserts the DONE
signal.

Change the example duration before deploying:

```python
# months, days, hours, minutes, seconds
hypnos.sleep((0, 0, 0, 10, 0))  # wake in 10 minutes
```

## API example

```python
from machine import I2C, Pin
from hypnos import Hypnos


i2c = I2C(0, sda=Pin(20, Pin.PULL_UP), scl=Pin(21, Pin.PULL_UP))
done = Pin(22, Pin.OUT)

hypnos = Hypnos(i2c, done)
hypnos.start()
print(hypnos.time)
print(hypnos.status())
hypnos.sleep((0, 0, 0, 0, 5))
```

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

## Licensing

Hibouonics-owned code in this repository is marked as proprietary under the root
`LICENSE` unless Hibouonics chooses a different release license later.
Third-party driver code remains under its original terms. Review
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) before making the repository
public.
