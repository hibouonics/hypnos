# Third-Party Notices

This repository includes or derives from third-party embedded drivers. Their
original notices should remain with the corresponding source files.

## PMS5003 driver

`drivers/pms5003.py` carries an MIT License notice naming Pimoroni Ltd., Kevin J.
Walters, and Erik Hess. The notice in that source file must be retained.

## Waveshare e-paper driver

`drivers/epaper_4in2.py` identifies the Waveshare team as author and includes an
MIT-style permission notice in the source header. That notice must be retained.

## Waveshare OLED driver

[`drivers/oled_1inch3.py`](drivers/oled_1inch3.py) is adapted from Waveshare's
Pico OLED 1.3-inch SPI example in
[`waveshare/Pico_code`](https://github.com/waveshare/Pico_code).

- [Upstream source](https://github.com/waveshare/Pico_code/blob/c50bc57040a33ee9540e993a2bbe99bf6e621fbd/Python/Pico-OLED-1.3/Pico-OLED-1.3%28spi%29.py)
  at revision `c50bc57040a33ee9540e993a2bbe99bf6e621fbd`.
- [Upstream license](https://github.com/waveshare/Pico_code/blob/c50bc57040a33ee9540e993a2bbe99bf6e621fbd/LICENSE):
  GNU General Public License, version 3.
- [Included license text](licenses/Waveshare-Pico_code-GPL-3.0.txt), copied
  verbatim from that revision.

The local adaptation removes the standalone demonstration, uses `const()` for
pin definitions, reorders imports, and corrects the `balck` attribute to
`black`. Attribution and license references were added on 2026-10-12.

This driver retains its upstream GPL terms and is not covered by the root MIT
license. Keep its attribution and accompanying license when redistributing it.
