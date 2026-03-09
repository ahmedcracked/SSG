import re

from textnode import TextNode, TextType


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        text_parts = old_node.text.split(delimiter)
        if len(text_parts) % 2 == 0:
            raise ValueError("Invalid markdown syntax: opened sections not closed")

        for i in range(len(text_parts)):
            text = text_parts[i]
            # Skip empty strings (e.g., if a delimiter is at the start or end)
            if text == "":
                continue

            if i % 2 == 0:
                new_nodes.append(TextNode(text, TextType.TEXT))
            else:
                new_nodes.append(TextNode(text, text_type))

    return new_nodes


def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


# def extract_markdown_links(text):
#     return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def extract_markdown_links(text):
    """
    Extract markdown links of the form [text](url) while:
    - Ignoring image syntax that starts with '!' (e.g. ![alt](src))
    - Allowing nested brackets inside the link text (e.g. [a [b]](url))
    - Allowing parentheses in the URL by tracking balanced parens
    Returns a list of (text, url) tuples in the order found.
    """
    results = []
    i = 0
    length = len(text)

    while i < length:
        ch = text[i]
        # Look for '[' that is not an image ('!' immediately before)
        if ch == "[" and not (i > 0 and text[i - 1] == "!"):
            # parse balanced bracketed text
            start_text = i + 1
            depth = 1
            j = start_text
            while j < length and depth > 0:
                if text[j] == "[":
                    depth += 1
                elif text[j] == "]":
                    depth -= 1
                j += 1

            if depth == 0:
                # j is position after the matching ']'
                link_text = text[start_text : j - 1]

                # skip optional whitespace between ] and (
                k = j
                while k < length and text[k].isspace():
                    k += 1

                # require an opening '(' for a link
                if k < length and text[k] == "(":
                    start_url = k + 1
                    depth_p = 1
                    m = start_url
                    while m < length and depth_p > 0:
                        if text[m] == "(":
                            depth_p += 1
                        elif text[m] == ")":
                            depth_p -= 1
                        m += 1

                    if depth_p == 0:
                        # m is position after the matching ')'
                        url = text[start_url : m - 1]
                        results.append((link_text, url))
                        # advance i to continue after the ')'
                        i = m
                        continue
                    else:
                        # Unbalanced parentheses: treat as non-match; move on
                        i = j
                        continue
                else:
                    # No '(' after ']' -> not a link, continue scanning after ']'
                    i = j
                    continue
            else:
                # Unbalanced brackets: no closing ']' found; stop scanning
                break
        i += 1

    return results
