from __future__ import annotations

import unittest

from hohokhan.gratitude import should_react_to_thanks


class GratitudeTests(unittest.TestCase):
    def test_named_thanks_reacts(self) -> None:
        for text in ("مرسی هوهو", "ممنون هوهوخان", "دمت گرم هو هو خان"):
            self.assertTrue(should_react_to_thanks(text, replies_to_self=False))

    def test_reply_to_self_reacts_without_name(self) -> None:
        self.assertTrue(should_react_to_thanks("دستت درد نکنه", replies_to_self=True))

    def test_unrelated_thanks_does_not_react(self) -> None:
        self.assertFalse(should_react_to_thanks("مرسی داداش", replies_to_self=False))

    def test_name_without_thanks_does_not_react(self) -> None:
        self.assertFalse(should_react_to_thanks("هوهو بیا", replies_to_self=False))


if __name__ == "__main__":
    unittest.main()
