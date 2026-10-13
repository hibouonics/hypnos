# Changelog

Notable changes to Hibouonics Hypnos firmware and documentation.

## Unreleased

### Added

- User manual covering RTC setup, alarms, power-fail records, SRAM, the public
  API, troubleshooting, and known driver limitations.
- Host-side unit tests for time arithmetic and register access.
- Hardware and contribution guidance.
- Waveshare OLED attribution, upstream source references, and the GNU GPL
  version 3 license text.

### Changed

- Adopted the MIT license for Hibouonics-owned code; third-party drivers retain
  their original licenses.
- Updated the README with commissioning steps, usage examples, and links to
  the user manual.
- Refactored the Hypnos driver for clearer naming and validation.
- Preserved aliases for commonly used legacy method names.
- Changed status reporting to return structured data, with `print_status()` for
  serial debugging.
- Restricted alarm enable writes to the intended control bit.

### Removed

- Redundant `drivers/mcp7940.py` helper; RTC support is provided by
  `firmware/hypnos.py`.
- The `legacy/` directory and its obsolete development scripts.
- Internal maintenance guides from the public documentation.
