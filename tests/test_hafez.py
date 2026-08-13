from __future__ import annotations

import gzip
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

httpx = types.ModuleType("httpx")
httpx.HTTPError = Exception
httpx.AsyncClient = object
sys.modules.setdefault("httpx", httpx)

from hohokhan.services.hafez import (
    load_hafez_corpus,
)


class HafezCorpusTests(unittest.TestCase):
    def test_complete_local_corpus_is_accepted(self) -> None:
        rows = [
            {"number": number, "poem": f"غزل {number}", "interpretation": "تعبیر"}
            for number in range(1, 496)
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "hafez.json.gz"
            with gzip.open(path, "wt", encoding="utf-8") as output:
                json.dump(rows, output, ensure_ascii=False)
            fortunes = load_hafez_corpus(path)
        self.assertEqual(len(fortunes), 495)
        self.assertEqual(fortunes[64].number, 65)

    def test_incomplete_local_corpus_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "hafez.json.gz"
            with gzip.open(path, "wt", encoding="utf-8") as output:
                output.write("[]")
            with self.assertRaises(ValueError):
                load_hafez_corpus(path)


if __name__ == "__main__":
    unittest.main()
