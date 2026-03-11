import os
import shutil

from block_markdown import markdown_to_html_node


def extract_title(markdown: str):
    lines = markdown.split("\n")
    header = lines[0]
    if header.startswith("# "):
        return header.lstrip("# ").rstrip(" ")
    else:
        raise Exception("No header in markdown")


def copy_files_recursive(source_dir_path, dest_dir_path):
    if not os.path.exists(dest_dir_path):
        os.mkdir(dest_dir_path)

    for filename in os.listdir(source_dir_path):
        from_path = os.path.join(source_dir_path, filename)
        dest_path = os.path.join(dest_dir_path, filename)
        print(f" * {from_path} -> {dest_path}")
        if os.path.isfile(from_path):
            shutil.copy(from_path, dest_path)
        else:
            copy_files_recursive(from_path, dest_path)


def generate_page(from_path, template_path, dest_path):
    print(f"*** Generating page from {from_path} to {dest_path} using {template_path}")
    dest_dir_path = os.path.dirname(dest_path)
    if dest_dir_path != "":
        os.makedirs(dest_dir_path, exist_ok=True)
    from_file, temp_file, dest_file = (
        open(from_path),
        open(template_path),
        open(dest_path, mode="w"),
    )
    from_content, temp_content = from_file.read(), temp_file.read()
    title = extract_title(from_content)
    html_string = markdown_to_html_node(from_content).to_html()
    final_html = temp_content.replace("{{ Title }}", title).replace(
        "{{ Content }}", html_string
    )

    dest_file.write(final_html)
    from_file.close()
    temp_file.close()
    dest_file.close()
