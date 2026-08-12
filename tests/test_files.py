from __future__ import annotations

import unittest

from hohokhan.utils.files import safe_filename


class FileHelperTests(unittest.TestCase):
    def test_path_traversal_is_removed(self) -> None:
        self.assertEqual(safe_filename("../../secret?.mp3"), "secret_.mp3")

    def test_empty_name_uses_fallback(self) -> None:
        self.assertEqual(safe_filename("../"), "download")


if __name__ == "__main__":
    unittest.main()
