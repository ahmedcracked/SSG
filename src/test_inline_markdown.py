import unittest

from inline_markdown import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
)
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

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_images_end(self):
        node = TextNode("start ![img](u)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("start ", TextType.TEXT),
            TextNode("img", TextType.IMAGE, "u"),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_images_two_images_only(self):
        node = TextNode("![a](u1)![b](u2)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("a", TextType.IMAGE, "u1"),
            TextNode("b", TextType.IMAGE, "u2"),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_images_not_image_like(self):
        node = TextNode("not an image ![a] (u)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual(new_nodes, [node])

    def test_split_links_basic(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("This is text with a link ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.TEXT),
            TextNode(
                "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
            ),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_links_adjacent(self):
        node = TextNode("a [x](u1)[y](u2) b", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("a ", TextType.TEXT),
            TextNode("x", TextType.LINK, "u1"),
            TextNode("y", TextType.LINK, "u2"),
            TextNode(" b", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_links_start_end(self):
        node = TextNode("[start](u) middle [end](v)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("start", TextType.LINK, "u"),
            TextNode(" middle ", TextType.TEXT),
            TextNode("end", TextType.LINK, "v"),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_links_no_links_returns_original(self):
        node = TextNode("no links here", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual(new_nodes, [node])

    def test_split_links_preserve_non_text(self):
        node = TextNode("[a](u)", TextType.TEXT)
        bold_node = TextNode("b", TextType.BOLD)
        new_nodes = split_nodes_link([node, bold_node])
        expected = [TextNode("a", TextType.LINK, "u"), bold_node]
        self.assertListEqual(new_nodes, expected)

    def test_split_links_ignores_images(self):
        node = TextNode("here ![i](u) and [link](v) done", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("here ![i](u) and ", TextType.TEXT),
            TextNode("link", TextType.LINK, "v"),
            TextNode(" done", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_images_multiple_nodes(self):
        n1 = TextNode("before ![a](u) mid", TextType.TEXT)
        n2 = TextNode("after ![b](v)", TextType.TEXT)
        new_nodes = split_nodes_image([n1, n2])
        expected = [
            TextNode("before ", TextType.TEXT),
            TextNode("a", TextType.IMAGE, "u"),
            TextNode(" mid", TextType.TEXT),
            TextNode("after ", TextType.TEXT),
            TextNode("b", TextType.IMAGE, "v"),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_links_multiple_nodes(self):
        n1 = TextNode("before [a](u) mid", TextType.TEXT)
        n2 = TextNode("after [b](v)", TextType.TEXT)
        new_nodes = split_nodes_link([n1, n2])
        expected = [
            TextNode("before ", TextType.TEXT),
            TextNode("a", TextType.LINK, "u"),
            TextNode(" mid", TextType.TEXT),
            TextNode("after ", TextType.TEXT),
            TextNode("b", TextType.LINK, "v"),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_images_with_space_between_bracket_and_paren_no_match(self):
        # extract_markdown_images uses a strict regex that does not allow spaces between ] and (
        node = TextNode("This is ![a] (u) done", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        # No image should be found; original node returned
        self.assertListEqual(new_nodes, [node])

    def test_split_links_empty_anchor_and_url(self):
        node = TextNode("[]()", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [TextNode("", TextType.LINK, "")]
        self.assertListEqual(new_nodes, expected)

    def test_split_images_empty_alt_and_url(self):
        node = TextNode("![]()", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [TextNode("", TextType.IMAGE, "")]
        self.assertListEqual(new_nodes, expected)

    def test_split_links_same_anchor_multiple(self):
        node = TextNode("a [x](u1) b [x](u2) c", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("a ", TextType.TEXT),
            TextNode("x", TextType.LINK, "u1"),
            TextNode(" b ", TextType.TEXT),
            TextNode("x", TextType.LINK, "u2"),
            TextNode(" c", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_images_with_brackets_in_alt_no_match(self):
        # Images with nested brackets in alt text are not matched by the simple regex
        node = TextNode("here ![a [b]](u) done", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        # No image matched, so original node is returned
        self.assertListEqual(new_nodes, [node])

    def test_split_links_preserve_image_markdown(self):
        node = TextNode("before ![img](u) middle [link](v) tail", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("before ![img](u) middle ", TextType.TEXT),
            TextNode("link", TextType.LINK, "v"),
            TextNode(" tail", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_images_preserve_link_markdown(self):
        node = TextNode("before [link](u) middle ![img](v) tail", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("before [link](u) middle ", TextType.TEXT),
            TextNode("img", TextType.IMAGE, "v"),
            TextNode(" tail", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_links_no_parenthesis_no_match(self):
        node = TextNode("here [a] no paren", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual(new_nodes, [node])

    def test_split_links_similar_anchor_text(self):
        node = TextNode("a [x](u1) x [y](u2) end", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("a ", TextType.TEXT),
            TextNode("x", TextType.LINK, "u1"),
            TextNode(" x ", TextType.TEXT),
            TextNode("y", TextType.LINK, "u2"),
            TextNode(" end", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)


class TestExtraction(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_links(self):
        text = "Check [boot.dev](https://boot.dev) and [example](http://example.com)"
        matches = extract_markdown_links(text)
        expected = [("boot.dev", "https://boot.dev"), ("example", "http://example.com")]
        self.assertListEqual(matches, expected)

    def test_links_and_images_mixed(self):
        s = "Here is ![an image](https://img) and a [link](https://link)"
        images = extract_markdown_images(s)
        links = extract_markdown_links(s)
        self.assertListEqual(images, [("an image", "https://img")])
        self.assertListEqual(links, [("link", "https://link")])

    def test_no_links_returns_empty(self):
        self.assertListEqual(extract_markdown_links("no links here"), [])

    def test_image_with_empty_alt_or_url(self):
        # Images with empty alt or src still match; regex should return empty strings for groups if present
        s1 = "Empty alt: ![](https://img1)"
        s2 = "Empty src: ![alt]()"
        m1 = extract_markdown_images(s1)
        m2 = extract_markdown_images(s2)
        self.assertListEqual(m1, [("", "https://img1")])
        self.assertListEqual(m2, [("alt", "")])


if __name__ == "__main__":
    unittest.main()
