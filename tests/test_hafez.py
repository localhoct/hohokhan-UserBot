from __future__ import annotations

import sys
import types
import unittest

httpx = types.ModuleType("httpx")
httpx.HTTPError = Exception
httpx.AsyncClient = object
sys.modules.setdefault("httpx", httpx)

from hohokhan.services.hafez import parse_hafez_fortune


class HafezParserTests(unittest.TestCase):
    def test_html_payload_is_parsed(self) -> None:
        payload = "<h3>غزل</h3><p>بیت اول<br>بیت دوم</p><h3>تعبیر فال شما:</h3><p>صبر کن.</p>"
        fortune = parse_hafez_fortune(payload, 65)
        self.assertEqual(fortune.number, 65)
        self.assertEqual(fortune.poem, "بیت اول\nبیت دوم")
        self.assertEqual(fortune.interpretation, "صبر کن.")

    def test_malformed_payload_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_hafez_fortune("فقط یک متن", 1)


if __name__ == "__main__":
    unittest.main()
