# Development Guide

## Active code vs. reference code

New product work should target `firmware/hypnos.py` and small scripts in
`examples/`. The `legacy/` directory is retained for historical context only.

## Style

- Use four spaces for Python indentation.
- Prefer descriptive snake_case names for functions and variables.
- Keep MicroPython compatibility in the active firmware.
- Avoid adding dependencies unless they are necessary on the device.
- Keep hardware pin assignments near the top of entry-point files.
- Raise specific exceptions for invalid API input instead of printing `error`.
- Do not commit generated firmware images or build directories.

## Testing

Run host-side logic tests with:

```bash
python -m unittest discover -s tests -v
```

A successful host test does **not** replace testing on the real RTC and power
hardware. Any change to I2C registers, alarm configuration, pin behavior, or
power sequencing needs physical validation.

## Releasing

Before a public release:

1. Search the entire Git history for credentials and tokens.
2. Verify third-party licenses and retain their notices.
3. Confirm all examples match the production PCB pinout.
4. Run host tests and device smoke tests.
5. Tag the release using semantic versioning once a public versioning policy is
   adopted.
