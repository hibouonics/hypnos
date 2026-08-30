# GitHub Publishing Checklist

Recommended repository name: `hibouonics-hypnos`.

Before making the repository public:

1. Confirm the product name, hardware revision, and README description are ready
   for public disclosure.
2. Rotate any Wi-Fi password or WeatherFlow token that appeared in the original
   development archive if it is still active.
3. Verify the redistribution terms for `drivers/oled_1inch3.py` and
   `drivers/mcp7940.py`; remove either file if provenance cannot be confirmed.
4. Choose whether the repository should remain proprietary (current root
   `LICENSE`) or be released under an open-source license.
5. Enable GitHub secret scanning and push protection when available.
6. Protect the default branch and require the `tests` workflow before merging.
7. Add a short repository description, topics such as `micropython`,
   `raspberry-pi-pico`, `embedded`, `rtc`, and `low-power`, and the Hibouonics
   company/project website if one exists.
8. Create a release/tag only after validating the firmware on the intended
   hardware revision.

## Suggested first commit

```text
Prepare Hibouonics Hypnos firmware for GitHub
```

## Suggested repository description

```text
MicroPython firmware and hardware drivers for the Hibouonics Hypnos low-power controller.
```
