from enum import Enum

from htmlnode import LeafNode


class TextType(Enum):
    TEXT = "text"  # plain text
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class TextNode:
    def __init__(self, text: str, text_type: TextType, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        return (
            isinstance(other, TextNode)
            and self.text_type == other.text_type
            and self.text == other.text
            and self.url == other.url
        )

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"


def text_node_to_html_node(textnode: TextNode):
    match textnode.text_type:
        case TextType.TEXT:
            return LeafNode(None, textnode.text)
        case TextType.BOLD:
            return LeafNode("b", textnode.text)
        case TextType.ITALIC:
            return LeafNode("i", textnode.text)
        case TextType.CODE:
            return LeafNode("code", textnode.text)
        case TextType.LINK:
            # Only include href if a URL was provided
            if textnode.url is None:
                return LeafNode("a", textnode.text)
            return LeafNode("a", textnode.text, {"href": textnode.url})
        case TextType.IMAGE:
            # Include src only if provided; always include alt
            if textnode.url is None:
                return LeafNode("img", "", {"alt": textnode.text})
            return LeafNode("img", "", {"src": textnode.url, "alt": textnode.text})
        case _:
            raise Exception("Unknown TextType Enum")


def text_to_textnodes(text):
    """
    Convert a plain string into a list of TextNode objects, applying inline
    markdown splitting. The imports for the inline_markdown helpers are done
    lazily here to avoid a circular import: inline_markdown imports TextNode /
    TextType from this module.
    """
    # Import here to defer until this function is called (breaks circular import).
    from inline_markdown import (
        split_nodes_delimiter,
        split_nodes_image,
        split_nodes_link,
    )

    result = [TextNode(text, TextType.TEXT)]
    result = split_nodes_delimiter(result, "**", TextType.BOLD)
    result = split_nodes_delimiter(result, "_", TextType.ITALIC)
    result = split_nodes_delimiter(result, "`", TextType.CODE)
    result = split_nodes_image(result)
    result = split_nodes_link(result)

    return result
