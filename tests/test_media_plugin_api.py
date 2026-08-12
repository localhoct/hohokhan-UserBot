from __future__ import annotations

import ast
import unittest
from pathlib import Path


class MediaPluginApiTests(unittest.TestCase):
    def test_reply_media_calls_only_use_supported_keywords(self) -> None:
        source = Path("hohokhan/plugins/media.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            if node.func.attr not in {"reply_audio", "reply_video"}:
                continue
            keywords = {keyword.arg for keyword in node.keywords}
            self.assertNotIn("file_name", keywords)


if __name__ == "__main__":
    unittest.main()
