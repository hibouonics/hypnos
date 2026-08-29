# Contributing

Thank you for helping improve Hebuonics Hypnos.

1. Create a focused branch for the change.
2. Keep product firmware changes in `firmware/` and reusable hardware support in
   `drivers/`.
3. Add or update tests when changing hardware-independent logic.
4. Run `python -m unittest discover -s tests -v` before opening a pull request.
5. Describe any hardware used to validate the change.
6. Never include credentials, tokens, generated build output, or local IDE
   files.

Changes to power sequencing, RTC register behavior, or hardware pin assignments
should include real-device validation notes in the pull request.
