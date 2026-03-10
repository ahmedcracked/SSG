import re
from enum import Enum

from htmlnode import LeafNode, ParentNode
from textnode import text_node_to_html_node, text_to_textnodes


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


# We are assuming that markdown is well-written, meaning, there's a single blank line between every block and the other.
def markdown_to_blocks(markdown_text: str) -> list[str]:
    blocks = markdown_text.split("\n\n")
    final_blocks = []
    for block in blocks:
        if block == "" or block == "\n":
            continue

        final_blocks.append(block.strip())

    return final_blocks


def block_to_block_type(block: str):
    if re.match(r"^(#{1,6})\s+(.*)$", block) is not None:
        return BlockType.HEADING
    elif block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE
    else:
        lines = block.split("\n")
        is_quote = True
        is_ol = True
        is_ul = True
        line_counter = 1
        for line in lines:
            if not line.startswith(">"):
                is_quote = False
            if not line.startswith("- "):
                is_ul = False
            if not line.startswith(f"{line_counter}. "):
                is_ol = False
            line_counter += 1

        if is_quote:
            return BlockType.QUOTE
        if is_ol:
            return BlockType.ORDERED_LIST
        if is_ul:
            return BlockType.UNORDERED_LIST

        return BlockType.PARAGRAPH


def text_to_html_children(text: str):
    textnodes = text_to_textnodes(text)
    return [text_node_to_html_node(tn) for tn in textnodes]


def markdown_to_html_node(markdown_text: str):
    blocks = markdown_to_blocks(markdown_text)
    block_nodes = []
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.PARAGRAPH:
            lines = block.split("\n")
            text = " ".join(line.strip() for line in lines if line.strip())
            if text:
                children = text_to_html_children(text)
                block_node = ParentNode("p", children)
            else:
                continue
        elif block_type == BlockType.HEADING:
            match = re.match(r"^(#{1,6})\s+(.*)$", block)
            level = len(match.group(1))
            text = match.group(2)
            children = text_to_html_children(text)
            block_node = ParentNode(f"h{level}", children)
        elif block_type == BlockType.CODE:
            code_text = block[4:-3].rstrip()
            lines = code_text.split("\n")
            if lines:
                min_indent = min(
                    (len(line) - len(line.lstrip()) for line in lines if line.strip()),
                    default=0,
                )
                code_text = "\n".join(line[min_indent:] for line in lines) + "\n"
            block_node = ParentNode("pre", [LeafNode("code", code_text)])
        elif block_type == BlockType.QUOTE:
            lines = block.split("\n")
            quote_lines = []
            for line in lines:
                if line.startswith("> "):
                    quote_lines.append(line[2:])
                elif line.startswith(">"):
                    quote_lines.append(line[1:])
            quote_text = " ".join(quote_lines)
            children = text_to_html_children(quote_text)
            block_node = ParentNode("blockquote", children)
        elif block_type == BlockType.UNORDERED_LIST:
            lines = block.split("\n")
            li_nodes = []
            for line in lines:
                if line.startswith("- "):
                    item_text = line[2:]
                    children = text_to_html_children(item_text)
                    li_nodes.append(ParentNode("li", children))
            block_node = ParentNode("ul", li_nodes)
        elif block_type == BlockType.ORDERED_LIST:
            lines = block.split("\n")
            li_nodes = []
            for i, line in enumerate(lines):
                expected = f"{i + 1}. "
                if line.startswith(expected):
                    item_text = line[len(expected) :]
                    children = text_to_html_children(item_text)
                    li_nodes.append(ParentNode("li", children))
            block_node = ParentNode("ol", li_nodes)
        block_nodes.append(block_node)
    return ParentNode("div", block_nodes)
