# Changelog

All notable changes to the cleaned Hebuonics Hypnos firmware repository will be
documented here.

## Unreleased

### Added
- GitHub-ready repository structure and documentation.
- Host-side unit tests for time arithmetic and register access.
- Security, contribution, hardware, and development guidance.

### Changed
- Refactored the Hypnos driver for clearer naming and validation.
- Preserved aliases for commonly used legacy method names.
- Changed status reporting to return structured data, with `print_status()` for
  serial debugging.
- Restricted alarm enable writes to the intended control bit.

### Security
- Removed hard-coded Wi-Fi credentials and WeatherFlow API tokens from the
  publishable repository.
- Excluded nested repositories, build output, archives, and OS metadata.
