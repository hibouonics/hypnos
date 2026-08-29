# Third-Party Notices

This repository includes or derives from third-party embedded drivers. Their
original notices should remain with the corresponding source files.

## PMS5003 driver

`drivers/pms5003.py` carries an MIT License notice naming Pimoroni Ltd., Kevin J.
Walters, and Erik Hess. The notice in that source file must be retained.

## Waveshare e-paper driver

`drivers/epaper_4in2.py` identifies the Waveshare team as author and includes an
MIT-style permission notice in the source header. That notice must be retained.

## OLED driver

`drivers/oled_1inch3.py` originated in the existing project files and appears to
be hardware-vendor example code. The source archive did not include a license
header in that file. Before redistributing this driver publicly, Hebuonics
should verify the original vendor source and redistribution terms. If licensing
cannot be confirmed, exclude this file from a public release and document the
external dependency instead.

## MCP7940 helper

`drivers/mcp7940.py` originated in the existing project files without a clear
license header. The active Hebuonics firmware does not require this helper
because `firmware/hypnos.py` directly implements the RTC functionality. It is
retained only as a reference driver; verify its provenance before public
redistribution or remove it from a public release.
