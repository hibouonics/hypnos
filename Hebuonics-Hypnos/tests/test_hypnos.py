import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "firmware" / "hypnos.py"
spec = importlib.util.spec_from_file_location("hypnos", MODULE_PATH)
hypnos_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hypnos_module)
Hypnos = hypnos_module.Hypnos


class FakeI2C:
    def __init__(self):
        self.registers = bytearray(256)

    def readfrom_mem(self, address, register, length):
        if address != Hypnos.ADDRESS:
            raise AssertionError("unexpected I2C address")
        return bytes(self.registers[register:register + length])

    def writeto_mem(self, address, register, data):
        if address != Hypnos.ADDRESS:
            raise AssertionError("unexpected I2C address")
        self.registers[register:register + len(data)] = data


class FakePin:
    def __init__(self):
        self.state = 0

    def high(self):
        self.state = 1

    def low(self):
        self.state = 0


class HypnosTests(unittest.TestCase):
    def setUp(self):
        self.i2c = FakeI2C()
        self.pin = FakePin()
        self.hypnos = Hypnos(self.i2c, self.pin)

    def test_bcd_round_trip(self):
        for value in (0, 1, 9, 10, 42, 59, 99):
            encoded = self.hypnos._decimal_to_bcd(value)
            self.assertEqual(self.hypnos._bcd_to_decimal(encoded), value)

    def test_time_round_trip(self):
        value = (2026, 8, 29, 10, 30, 45, 5)
        self.hypnos.time = value
        self.assertEqual(self.hypnos.time, value)

    def test_add_time_across_leap_day(self):
        result = self.hypnos._add_time(
            (2024, 2, 29, 23, 59, 30, 3),
            (0, 0, 0, 0, 31),
        )
        self.assertEqual(result[:6], (2024, 3, 1, 0, 0, 1))

    def test_add_month_clamps_day(self):
        result = self.hypnos._add_time(
            (2025, 1, 31, 12, 0, 0, 4),
            (1, 0, 0, 0, 0),
        )
        self.assertEqual(result[:6], (2025, 2, 28, 12, 0, 0))

    def test_sram_bounds(self):
        self.hypnos.set_memory(63, 255)
        self.assertEqual(self.hypnos.get_memory(63), b"\xff")
        with self.assertRaises(ValueError):
            self.hypnos.set_memory(64, 1)
        with self.assertRaises(ValueError):
            self.hypnos.get_memory(63, 2)

    def test_alarm_enable_preserves_other_control_bits(self):
        self.i2c.registers[0x07] = 0b10100101
        self.hypnos.enable_alarm()
        self.assertEqual(self.i2c.registers[0x07], 0b10110101)
        self.hypnos.disable_alarm()
        self.assertEqual(self.i2c.registers[0x07], 0b10100101)

    def test_sleep_sets_alarm_and_done(self):
        self.hypnos.time = (2026, 8, 29, 10, 0, 0, 5)
        self.hypnos.sleep((0, 0, 0, 0, 5))
        self.assertEqual(self.hypnos.alarm[:5], (8, 29, 10, 0, 5))
        self.assertEqual(self.pin.state, 1)
        self.assertTrue(self.hypnos.alarm_enabled())

    def test_invalid_sleep_duration(self):
        with self.assertRaises(ValueError):
            self.hypnos.sleep((0, 1))
        with self.assertRaises(ValueError):
            self.hypnos.sleep((0, 0, 0, 0, -1))


if __name__ == "__main__":
    unittest.main()
