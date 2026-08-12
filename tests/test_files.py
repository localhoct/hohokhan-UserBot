from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from hohokhan.utils.files import find_downloaded_media, safe_filename


class FileHelperTests(unittest.TestCase):
    def test_path_traversal_is_removed(self) -> None:
        self.assertEqual(safe_filename("../../secret?.mp3"), "secret_.mp3")

    def test_empty_name_uses_fallback(self) -> None:
        self.assertEqual(safe_filename("../"), "download")

    def test_final_media_is_found_in_nested_directory(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            nested = root / "postprocessed"
            nested.mkdir()
            (root / "cover.webp").write_bytes(b"image")
            (root / "audio.part").write_bytes(b"partial")
            expected = nested / "song.mp3"
            expected.write_bytes(b"audio")
            self.assertEqual(find_downloaded_media(root, attempts=1), expected)

    def test_empty_output_is_rejected(self) -> None:
        with TemporaryDirectory() as directory, self.assertRaises(FileNotFoundError):
            find_downloaded_media(Path(directory), attempts=1)


if __name__ == "__main__":
    unittest.main()
