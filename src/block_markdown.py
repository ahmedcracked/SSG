def markdown_to_blocks(markdown_text: str):
    blocks = markdown_text.split("\n\n")
    final_blocks = []
    for block in blocks:
        if block == "" or block == "\n":
            continue

        final_blocks.append(block.strip())

    return final_blocks
