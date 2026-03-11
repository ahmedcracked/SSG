import unittest

from functions import extract_title


class TestExtractTitle(unittest.TestCase):
    def test_no_newline(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_newline(self):
        self.assertEqual(extract_title("# Hi\n\n> This is a quote"), "Hi")

    def test_trailing_spaces(self):
        self.assertEqual(extract_title("# Hello  "), "Hello")

    def test_leading_spaces_after_hash(self):
        self.assertEqual(extract_title("#  Hello"), "Hello")

    def test_no_space_after_hash(self):
        with self.assertRaises(Exception):
            extract_title("#Hello")

    def test_empty_title(self):
        self.assertEqual(extract_title("# "), "")

    def test_no_header(self):
        with self.assertRaises(Exception):
            extract_title("Hello world")

    def test_empty_string(self):
        with self.assertRaises(Exception):
            extract_title("")

    def test_only_newlines(self):
        with self.assertRaises(Exception):
            extract_title("\n\n")

    def test_hash_only(self):
        with self.assertRaises(Exception):
            extract_title("#")


if __name__ == "__main__":
    unittest.main()
