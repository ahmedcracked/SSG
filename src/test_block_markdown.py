import unittest

from block_markdown import (
    BlockType,
    block_to_block_type,
    markdown_to_blocks,
    markdown_to_html_node,
)


class TestMarkdownToHTML(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_newlines(self):
        md = """
This is **bolded** paragraph




This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_block_to_block_type_heading(self):
        # Valid headings
        self.assertEqual(block_to_block_type("# Heading"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("## Subheading"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("### Level 3"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("#### Level 4"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("##### Level 5"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("###### Level 6"), BlockType.HEADING)
        # Invalid: too many #
        self.assertEqual(block_to_block_type("####### Invalid"), BlockType.PARAGRAPH)
        # Invalid: no space
        self.assertEqual(block_to_block_type("#Heading"), BlockType.PARAGRAPH)

    def test_block_to_block_type_code(self):
        # Valid code block
        self.assertEqual(block_to_block_type("```\ncode here\n```"), BlockType.CODE)
        # Invalid: no newline after ```
        self.assertEqual(block_to_block_type("```code```"), BlockType.PARAGRAPH)
        # Invalid: doesn't end with ```
        self.assertEqual(block_to_block_type("```\ncode"), BlockType.PARAGRAPH)

    def test_block_to_block_type_quote(self):
        # Valid quote
        self.assertEqual(block_to_block_type("> line1\n> line2"), BlockType.QUOTE)
        # Valid without space
        self.assertEqual(block_to_block_type(">line1\n>line2"), BlockType.QUOTE)
        # Invalid: not all lines start with >
        self.assertEqual(block_to_block_type("line1\n> line2"), BlockType.PARAGRAPH)
        # Single line
        self.assertEqual(block_to_block_type("> single quote"), BlockType.QUOTE)

    def test_block_to_block_type_unordered_list(self):
        # Valid unordered list
        self.assertEqual(
            block_to_block_type("- item1\n- item2"), BlockType.UNORDERED_LIST
        )
        # Invalid: no space after -
        self.assertEqual(block_to_block_type("-item1"), BlockType.PARAGRAPH)
        # Invalid: not all lines
        self.assertEqual(block_to_block_type("- item1\nitem2"), BlockType.PARAGRAPH)
        # Single line
        self.assertEqual(block_to_block_type("- single item"), BlockType.UNORDERED_LIST)

    def test_block_to_block_type_ordered_list(self):
        # Valid ordered list
        self.assertEqual(
            block_to_block_type("1. item1\n2. item2"), BlockType.ORDERED_LIST
        )
        # Invalid: doesn't start at 1
        self.assertEqual(block_to_block_type("2. item1"), BlockType.PARAGRAPH)
        # Invalid: skips number
        self.assertEqual(block_to_block_type("1. item1\n3. item2"), BlockType.PARAGRAPH)
        # Invalid: no space after .
        self.assertEqual(block_to_block_type("1.item1"), BlockType.PARAGRAPH)
        # Single line
        self.assertEqual(block_to_block_type("1. single item"), BlockType.ORDERED_LIST)

    def test_block_to_block_type_paragraph(self):
        # Plain text
        self.assertEqual(
            block_to_block_type("This is a paragraph."), BlockType.PARAGRAPH
        )
        # Mixed content not matching other types
        self.assertEqual(
            block_to_block_type("Some text\nMore text"), BlockType.PARAGRAPH
        )

    def test_paragraphs(self):
        md = """
    This is **bolded** paragraph
    text in a p
    tag here

    This is another paragraph with _italic_ text and `code` here

    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
    ```
    This is text that _should_ remain
    the **same** even with inline stuff
    ```
    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_markdown_to_html_node(self):
        md = "# Heading\n\nThis is a paragraph."
        node = markdown_to_html_node(md)
        self.assertEqual(node.tag, "div")
        self.assertEqual(len(node.children), 2)
        self.assertEqual(node.children[0].tag, "h1")
        self.assertEqual(node.children[1].tag, "p")
        # Check HTML output
        expected_html = "<div><h1>Heading</h1><p>This is a paragraph.</p></div>"
        self.assertEqual(node.to_html(), expected_html)

    def test_heading(self):
        md = "## Subheading with **bold**"
        node = markdown_to_html_node(md)
        expected = "<div><h2>Subheading with <b>bold</b></h2></div>"
        self.assertEqual(node.to_html(), expected)

    def test_quote(self):
        md = "> This is a quote\n> With `code`"
        node = markdown_to_html_node(md)
        expected = (
            "<div><blockquote>This is a quote With <code>code</code></blockquote></div>"
        )
        self.assertEqual(node.to_html(), expected)

    def test_unordered_list(self):
        md = "- Item 1\n- Item 2 with _italic_"
        node = markdown_to_html_node(md)
        expected = (
            "<div><ul><li>Item 1</li><li>Item 2 with <i>italic</i></li></ul></div>"
        )
        self.assertEqual(node.to_html(), expected)

    def test_ordered_list(self):
        md = "1. First item\n2. Second item"
        node = markdown_to_html_node(md)
        expected = "<div><ol><li>First item</li><li>Second item</li></ol></div>"
        self.assertEqual(node.to_html(), expected)

    def test_mixed_blocks(self):
        md = "# Title\n\n> A quote here\n\n- List item\n\nThis is a paragraph."
        node = markdown_to_html_node(md)
        expected = "<div><h1>Title</h1><blockquote>A quote here</blockquote><ul><li>List item</li></ul><p>This is a paragraph.</p></div>"
        self.assertEqual(node.to_html(), expected)

    def test_empty_markdown(self):
        md = ""
        node = markdown_to_html_node(md)
        expected = "<div></div>"
        self.assertEqual(node.to_html(), expected)


if __name__ == "__main__":
    unittest.main()
