from __future__ import annotations

import unittest

from hohokhan.commands import admin_say_text, weather_city


class CommandParsingTests(unittest.TestCase):
    def test_weather_prefixes_are_fully_removed(self) -> None:
        self.assertEqual(weather_city("آب و هوای tehran"), "tehran")
        self.assertEqual(weather_city("آب و هوا تهران"), "تهران")
        self.assertEqual(weather_city("هوای شیراز"), "شیراز")
        self.assertEqual(weather_city(".weather Berlin"), "Berlin")

    def test_admin_say_extracts_only_the_payload(self) -> None:
        self.assertEqual(admin_say_text("هوهوخان بگو سلام هوهو"), "سلام هوهو")
        self.assertEqual(admin_say_text("هو هو خان بگو سلام"), "سلام")
        self.assertIsNone(admin_say_text("بگو سلام"))


if __name__ == "__main__":
    unittest.main()
