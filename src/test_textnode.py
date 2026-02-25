import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq_same(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_ne_text(self):
        node = TextNode("one", TextType.TEXT)
        node2 = TextNode("two", TextType.TEXT)
        self.assertNotEqual(node, node2)

    def test_ne_type(self):
        node = TextNode("same text", TextType.TEXT)
        node2 = TextNode("same text", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_ne_url(self):
        node = TextNode("link text", TextType.LINK, "https://example.com")
        node2 = TextNode("link text", TextType.LINK, "https://other.com")
        self.assertNotEqual(node, node2)

    def test_eq_url_none(self):
        # both urls None -> equal
        node = TextNode("no url", TextType.LINK)
        node2 = TextNode("no url", TextType.LINK, None)
        self.assertEqual(node, node2)

    def test_repr_format(self):
        node = TextNode("This is a text node", TextType.BOLD)
        expected = "TextNode(This is a text node, bold, None)"
        self.assertEqual(repr(node), expected)

    def test_eq_with_ducktyped_object(self):
        # The equality implementation compares attributes, so a duck-typed object with same attrs compares equal
        class Dummy:
            def __init__(self, text, text_type, url):
                self.text = text
                self.text_type = text_type
                self.url = url

        node = TextNode("duck", TextType.CODE, "u")
        dummy = Dummy("duck", TextType.CODE, "u")
        # Since __eq__ uses attribute access, this should be False
        self.assertNotEqual(node, dummy)

    def test_empty_and_unicode_text(self):
        empty = TextNode("", TextType.TEXT)
        empty2 = TextNode("", TextType.TEXT)
        self.assertEqual(empty, empty2)

        uni = TextNode("日本語のテキスト", TextType.TEXT)
        uni2 = TextNode("日本語のテキスト", TextType.TEXT)
        self.assertEqual(uni, uni2)


if __name__ == "__main__":
    unittest.main()
