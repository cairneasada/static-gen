from util import markdown_to_html_node, extract_title
import os

def generate_page(basepath, from_path, template_path, dest_path):
    print(f'Generating path from {from_path} to {dest_path} using {template_path}')

    source = ''
    template = ''
    with open(from_path, encoding="utf-8") as f:
        source = f.read()
    
    with open(template_path, encoding="utf-8") as f:
        template = f.read()
    
    html = markdown_to_html_node(source).to_html()
    title = extract_title(source)

    contents = template.replace("{{ Title }}", title).replace("{{ Content }}", html).replace("href=\"/", f'href=\"{basepath}').replace("src=\"/", f'src=\"{basepath}')

    dest_dir = os.path.dirname(dest_path)
    os.makedirs(dest_dir, exist_ok=True)

    if os.path.exists(dest_path):
        raise ValueError(f'destination {dest_path} already exists')

    with open(dest_path, mode='x', encoding="utf-8") as f:
        f.write(contents)
    
def generate_pages_recursive(basepath, from_dir, template_path, to_dir):
    if not os.path.exists(from_dir):
        raise ValueError(f'source {from_dir} does not exist')
    
    os.makedirs(to_dir, exist_ok=True)

    for entry in os.listdir(from_dir):
        src_path = os.path.join(from_dir, entry)
        if os.path.isfile(src_path):
            # generate the file
            generate_page(basepath, src_path, template_path, os.path.join(to_dir, 'index.html'))
        else:
            # recurse
            generate_pages_recursive(basepath, src_path, template_path, os.path.join(to_dir, entry))

    



    