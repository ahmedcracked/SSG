import unittest

from inline_markdown import split_nodes_delimiter
from textnode import TextNode, TextType


class TestInlineMarkdown(unittest.TestCase):
    def test_delim_bold(self):
        node = TextNode("This is **bolded** text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bolded", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_delim_italic_single_char(self):
        node = TextNode("Make this _italic_ now", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        expected = [
            TextNode("Make this ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" now", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_delim_at_start_only(self):
        node = TextNode("**start** and more", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("start", TextType.BOLD),
            TextNode(" and more", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_delim_only_entire_string(self):
        node = TextNode("**only**", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [TextNode("only", TextType.BOLD)]
        self.assertListEqual(new_nodes, expected)

    def test_multiple_delimiters(self):
        node = TextNode("a **b** c **d** e", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("a ", TextType.TEXT),
            TextNode("b", TextType.BOLD),
            TextNode(" c ", TextType.TEXT),
            TextNode("d", TextType.BOLD),
            TextNode(" e", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_unmatched_delimiter_raises(self):
        node = TextNode("This is **not closed", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_non_text_nodes_are_preserved(self):
        # If a node is not plain TEXT, it should be left untouched by the splitter
        bold_node = TextNode("already bold", TextType.BOLD)
        new_nodes = split_nodes_delimiter([bold_node], "**", TextType.BOLD)
        # The exact same node instance is appended, but equality by value is sufficient here
        self.assertListEqual(new_nodes, [bold_node])

    def test_skip_empty_segments_between_adjacent_delimiters(self):
        # Adjacent delimiters like "****" may produce empty segments which should be skipped
        node = TextNode("before **** after", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        # The sequence splits into: "before ", "", " after" -> empty middle part is skipped
        expected = [
            TextNode("before ", TextType.TEXT),
            TextNode(" after", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_mixed_input_preserves_order(self):
        # Multiple nodes: a TEXT node that splits plus a non-TEXT node afterwards
        text_node = TextNode("one **two** three", TextType.TEXT)
        pre_bold = TextNode("preformatted", TextType.CODE)
        new_nodes = split_nodes_delimiter([text_node, pre_bold], "**", TextType.BOLD)
        expected = [
            TextNode("one ", TextType.TEXT),
            TextNode("two", TextType.BOLD),
            TextNode(" three", TextType.TEXT),
            pre_bold,
        ]
        self.assertListEqual(new_nodes, expected)


if __name__ == "__main__":
    unittest.main()
