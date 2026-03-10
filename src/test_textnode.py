import unittest

from textnode import (
    TextNode,
    TextType,
    text_node_to_html_node,
    text_to_textnodes,
)


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


class TestTextNodeToHTMLNode(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "bold text")
        self.assertEqual(html_node.props, None)

    def test_italic(self):
        node = TextNode("italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "italic text")
        self.assertEqual(html_node.props, None)

    def test_code(self):
        node = TextNode("code()", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "code()")
        self.assertEqual(html_node.props, None)

    def test_link_with_url(self):
        url = "https://example.com"
        node = TextNode("link text", TextType.LINK, url)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "link text")
        # href should be present in props (even if None in other cases)
        self.assertIsNotNone(html_node.props)
        self.assertIn("href", html_node.props)
        self.assertEqual(html_node.props.get("href"), url)

    # in TestTextNodeToHTMLNode
    def test_link_without_url(self):
        node = TextNode("link text", TextType.LINK, None)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "link text")
        # href should be omitted when no URL provided
        self.assertIsNone(html_node.props)

    def test_image_without_url(self):
        alt_text = "an image"
        node = TextNode(alt_text, TextType.IMAGE, None)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"alt": alt_text})

    def test_image(self):
        url = "https://img.example/1.png"
        alt_text = "an image"
        node = TextNode(alt_text, TextType.IMAGE, url)
        html_node = text_node_to_html_node(node)
        # Image mapping uses tag 'img', empty value, and props with src and alt
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertIsNotNone(html_node.props)
        self.assertEqual(html_node.props.get("src"), url)
        self.assertEqual(html_node.props.get("alt"), alt_text)

    def test_unknown_type_raises(self):
        # Passing an unknown TextType (or None) should raise the fallback Exception
        node = TextNode("x", None)
        with self.assertRaises(Exception):
            text_node_to_html_node(node)


class TestTextToTextnodes(unittest.TestCase):
    def test_text_to_textnodes_mixed(self):
        s = (
            "This is **text** with an _italic_ word and a `code block`"
            " and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a "
            "[link](https://boot.dev)"
        )
        nodes = text_to_textnodes(s)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode(
                "obi wan image",
                TextType.IMAGE,
                "https://i.imgur.com/fJRm4Vk.jpeg",
            ),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertListEqual(nodes, expected)

    def test_preserve_order(self):
        # Ensure the sequence of nodes returned preserves the original text order
        s = "start _I_ middle **B** `C` end"
        nodes = text_to_textnodes(s)
        expected = [
            TextNode("start ", TextType.TEXT),
            TextNode("I", TextType.ITALIC),
            TextNode(" middle ", TextType.TEXT),
            TextNode("B", TextType.BOLD),
            TextNode(" ", TextType.TEXT),
            TextNode("C", TextType.CODE),
            TextNode(" end", TextType.TEXT),
        ]
        self.assertListEqual(nodes, expected)

    def test_repeated_same_type_adjacent(self):
        # multiple bold sections adjacent with no text between: **** style
        s = "**a****b****c**"
        nodes = text_to_textnodes(s)
        expected = [
            TextNode("a", TextType.BOLD),
            TextNode("b", TextType.BOLD),
            TextNode("c", TextType.BOLD),
        ]
        self.assertListEqual(nodes, expected)

    def test_adjacent_elements_no_space(self):
        # Mix of link elements adjacent with no space; order should match original
        s = "A [x](u1)[y](u2)B"
        nodes = text_to_textnodes(s)
        expected = [
            TextNode("A ", TextType.TEXT),
            TextNode("x", TextType.LINK, "u1"),
            TextNode("y", TextType.LINK, "u2"),
            TextNode("B", TextType.TEXT),
        ]
        self.assertListEqual(nodes, expected)

    def test_touching_various_elements(self):
        # Elements touching each other without spaces and in different orders
        s = "[a](lu)![b](iu)`c`_d_**e**"
        nodes = text_to_textnodes(s)
        expected = [
            TextNode("a", TextType.LINK, "lu"),
            TextNode("b", TextType.IMAGE, "iu"),
            TextNode("c", TextType.CODE),
            TextNode("d", TextType.ITALIC),
            TextNode("e", TextType.BOLD),
        ]
        self.assertListEqual(nodes, expected)

    def test_image_then_link_touching(self):
        # Image followed immediately by link, no spaces
        s = "![img](iu)[link](lu)"
        nodes = text_to_textnodes(s)
        expected = [
            TextNode("img", TextType.IMAGE, "iu"),
            TextNode("link", TextType.LINK, "lu"),
        ]
        self.assertListEqual(nodes, expected)

    def test_mixed_adjacent_and_repeated(self):
        # A more complex mixture: adjacent bolds, touching link/image, followed by inline code
        s = "**a****b**![i](iu)[l](lu)`z`"
        nodes = text_to_textnodes(s)
        expected = [
            TextNode("a", TextType.BOLD),
            TextNode("b", TextType.BOLD),
            TextNode("i", TextType.IMAGE, "iu"),
            TextNode("l", TextType.LINK, "lu"),
            TextNode("z", TextType.CODE),
        ]
        self.assertListEqual(nodes, expected)


if __name__ == "__main__":
    unittest.main()
