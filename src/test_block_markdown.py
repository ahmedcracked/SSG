import unittest

from block_markdown import BlockType, block_to_block_type, markdown_to_blocks


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


if __name__ == "__main__":
    unittest.main()
