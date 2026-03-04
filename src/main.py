from textnode import TextNode
from textnode import TextType
from generate import generate_page, generate_pages_recursive
import os
import shutil

def main():
    copy_sources('static', 'public')
    generate_pages_recursive("content", "template.html", "public")

def copy_sources(source, dest):
    if os.path.exists(dest):
        print(f'destination "{dest}" exists')
        if os.path.isfile(dest):
            raise FileExistsError(f'"{dest} exists and is a file')
        else:
            print(f'cleaning up "{dest}"')
            shutil.rmtree(dest)
    os.mkdir(dest)
    do_copy(source, dest)

def do_copy(source_dir, dest_dir):
    print(f'getting entries for {source_dir}')
    for entry in os.listdir(source_dir):
        print(f'found entry {entry}')
        src_path = os.path.join(source_dir, entry)
        dest_path = os.path.join(dest_dir, entry)
        if os.path.isfile(src_path):
            print(f'copying file {src_path} to {dest_path}')
            shutil.copy(src_path, dest_path)
        else:
            print(f'processing directory {src_path}')
            os.mkdir(dest_path)
            do_copy(src_path, dest_path)


main()

