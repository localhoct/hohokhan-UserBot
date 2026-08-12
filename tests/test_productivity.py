import unittest

from hohokhan.productivity import format_duration, normalize_note_name


class ProductivityTests(unittest.TestCase):
    def test_duration_format(self) -> None:
        self.assertEqual(format_duration(45), "45 ثانیه")
        self.assertEqual(format_duration(3_661), "1 ساعت و 1 دقیقه")
        self.assertEqual(format_duration(90_000), "1 روز و 1 ساعت")

    def test_note_name_validation(self) -> None:
        self.assertEqual(normalize_note_name(" سرور-۱ "), "سرور-۱")
        for value in ("", "bad name", "../secret", "x" * 33):
            with self.assertRaises(ValueError):
                normalize_note_name(value)
