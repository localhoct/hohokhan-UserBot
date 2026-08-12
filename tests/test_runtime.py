import unittest

from hohokhan.runtime import validate_python


class RuntimeTests(unittest.TestCase):
    def test_supported_python_versions(self) -> None:
        for version in ((3, 11, 0), (3, 12, 9), (3, 13, 4), (3, 14, 0)):
            validate_python(version)

    def test_unsupported_python_versions(self) -> None:
        for version in ((3, 10, 9), (3, 15, 0), (4, 0, 0)):
            with self.assertRaises(RuntimeError):
                validate_python(version)
