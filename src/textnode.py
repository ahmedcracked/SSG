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
