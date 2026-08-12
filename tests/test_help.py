import unittest

from hohokhan.help import CATEGORIES, render_help


class HelpTests(unittest.TestCase):
    def test_all_help_pages_fit_telegram_limit(self) -> None:
        pages = render_help("all")
        self.assertEqual(len(pages), len(CATEGORIES))
        self.assertTrue(all(len(page) < 4_096 for page in pages))

    def test_help_contains_new_and_existing_commands(self) -> None:
        rendered = "\n".join(render_help("all"))
        for command in (".music", ".afk", ".save", ".purge", ".quote", ".kick"):
            self.assertIn(command, rendered)

    def test_persian_alias_resolves(self) -> None:
        page = render_help("مدیریت")[0]
        self.assertIn(".kick", page)

    def test_unknown_topic_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            render_help("does-not-exist")
