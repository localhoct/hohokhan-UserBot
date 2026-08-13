from __future__ import annotations

import unittest

from hohokhan.hafez_archive import archive_tag, archived_ghazal_number


class HafezArchiveTests(unittest.TestCase):
    def test_archive_tag_is_stable(self) -> None:
        self.assertEqual(archive_tag(65), "#غزل_65")

    def test_archive_caption_number_is_parsed(self) -> None:
        self.assertEqual(
            archived_ghazal_number("🪶 خوانش غزل حافظ\n#غزل_495 #حافظ"), 495
        )

    def test_invalid_or_unrelated_caption_is_ignored(self) -> None:
        self.assertIsNone(archived_ghazal_number("#غزل_496"))
        self.assertIsNone(archived_ghazal_number("غزل حافظ"))

    def test_invalid_number_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            archive_tag(0)


if __name__ == "__main__":
    unittest.main()
