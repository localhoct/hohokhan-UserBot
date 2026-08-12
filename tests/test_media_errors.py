from __future__ import annotations

import unittest

from hohokhan.media_errors import download_error_message


class MediaErrorTests(unittest.TestCase):
    def test_antibot_error_explains_missing_cookie(self) -> None:
        message = download_error_message(
            "Sign in to confirm you’re not a bot. Use --cookies-from-browser or --cookies",
            cookies_configured=False,
        )
        self.assertIn("YTDLP_COOKIES_FILE", message)

    def test_antibot_error_explains_expired_cookie(self) -> None:
        message = download_error_message(
            "Sign in to confirm you're not a bot",
            cookies_configured=True,
        )
        self.assertIn("منقضی", message)

    def test_other_errors_are_not_exposed(self) -> None:
        message = download_error_message("secret internal error", cookies_configured=False)
        self.assertNotIn("secret internal error", message)


if __name__ == "__main__":
    unittest.main()
