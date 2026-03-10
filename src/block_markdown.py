import re
from enum import Enum


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


# We are assuming that markdown is well-written, meaning, there's a single blank line between every block and the other.
def markdown_to_blocks(markdown_text: str):
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
