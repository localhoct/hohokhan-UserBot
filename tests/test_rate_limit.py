from __future__ import annotations

import unittest

from hohokhan.rate_limit import RateLimiter


class RateLimiterTests(unittest.TestCase):
    def test_penalty_after_limit(self) -> None:
        limiter = RateLimiter(messages=2, window_seconds=3, penalty_seconds=10)
        self.assertTrue(limiter.check(7, now=0).allowed)
        self.assertTrue(limiter.check(7, now=1).allowed)
        denied = limiter.check(7, now=2)
        self.assertFalse(denied.allowed)
        self.assertEqual(denied.retry_after, 10)
        self.assertFalse(limiter.check(7, now=5).allowed)
        self.assertTrue(limiter.check(7, now=13).allowed)

    def test_users_are_isolated(self) -> None:
        limiter = RateLimiter(messages=1, window_seconds=3, penalty_seconds=10)
        self.assertTrue(limiter.check(1, now=0).allowed)
        self.assertFalse(limiter.check(1, now=1).allowed)
        self.assertTrue(limiter.check(2, now=1).allowed)


if __name__ == "__main__":
    unittest.main()
