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


def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        links_list = extract_markdown_links(old_node.text)
        if len(links_list) == 0:
            new_nodes.append(old_node)
            continue

        current_node_text = old_node.text
        for i in range(len(links_list)):
            link = links_list[i]
            anchor_text = link[0]
            url = link[1]
            delimeter = f"[{anchor_text}]({url})"
            sections = current_node_text.split(delimeter, 1)
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(anchor_text, TextType.LINK, url))
            current_node_text = sections[1]

        if current_node_text != "":
            new_nodes.append(TextNode(current_node_text, TextType.TEXT))

    return new_nodes


def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        images_list = extract_markdown_images(old_node.text)
        if len(images_list) == 0:
            new_nodes.append(old_node)
            continue

        current_node_text = old_node.text
        for i in range(len(images_list)):
            image = images_list[i]
            alt_text = image[0]
            url = image[1]
            delimeter = f"![{alt_text}]({url})"
            sections = current_node_text.split(delimeter, 1)
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            current_node_text = sections[1]

        if current_node_text != "":
            new_nodes.append(TextNode(current_node_text, TextType.TEXT))

    return new_nodes


def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
