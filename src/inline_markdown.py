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
