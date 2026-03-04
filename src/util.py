import re
from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node
from enum import Enum

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
        else:
            pieces = node.text.split(delimiter, 2)
            count = len(pieces)
            if len(pieces) <= 1:
                if len(pieces[0]) > 0:
                    new_nodes.append(node)
            elif count % 2 == 1:
                if len(pieces[0]) > 0:
                    new_nodes.append(TextNode(pieces[0], TextType.TEXT))
                new_nodes.append(TextNode(pieces[1], text_type))
                new_nodes.extend(split_nodes_delimiter([TextNode(pieces[2], TextType.TEXT)], delimiter, text_type))
            else:
                raise ValueError(f'mismatched delimiter {delimiter} found in {node.text}')
    return new_nodes

def extract_markdown_images(text):
    pattern = "!\[([^\]]+)\]\(([^\)]+)\)"
    return re.findall(pattern, text)

def extract_markdown_links(text):
    pattern = "(?<!\!)\[([^\]]+)\]\(([^\)]+)\)"
    return re.findall(pattern, text)

def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        text = node.text
        images = extract_markdown_images(text)
        if len(images) == 0:
            new_nodes.append(node)
        else:
            for image in images:
                image_alt = image[0]
                image_link = image[1]
                segments = text.split(f"![{image_alt}]({image_link})", 1)
                if segments[0] != "":
                    new_nodes.append(TextNode(segments[0], TextType.TEXT))
                
                new_nodes.append(TextNode(image_alt, TextType.IMAGE, image_link))

                text = segments[1]
            if text != "":
                new_nodes.append(TextNode(text, TextType.TEXT))
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        text = node.text
        images = extract_markdown_links(text)
        if len(images) == 0:
            new_nodes.append(node)
        else:
            for image in images:
                image_alt = image[0]
                image_link = image[1]
                segments = text.split(f"[{image_alt}]({image_link})", 1)
                if segments[0] != "":
                    new_nodes.append(TextNode(segments[0], TextType.TEXT))
                
                new_nodes.append(TextNode(image_alt, TextType.LINK, image_link))

                text = segments[1]
            if text != "":
                new_nodes.append(TextNode(text, TextType.TEXT))
    return new_nodes

def text_to_textnodes(text):
    nodes = []
    if len(text) > 0:
        start = TextNode(text, TextType.TEXT)
        nodes = split_nodes_delimiter(
            split_nodes_delimiter( 
                split_nodes_delimiter([start], '**', TextType.BOLD), '_', TextType.ITALIC),
                '`', TextType.CODE)
        
        nodes = split_nodes_image(split_nodes_link(nodes))

    return nodes

def markdown_to_blocks(markdown):
    blocks = []
    l = markdown.split('\n\n')
    for block in l:
        txt = block.strip()
        if len(txt) > 0:
            blocks.append(txt)

    return blocks

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def block_to_block_type(block):
    type = BlockType.PARAGRAPH
    if len(block) > 0:
        lines = block.split('\n')
        line_count = len(lines)
        if line_count > 0:
            if line_count == 1 and re.match("^#+ ", lines[0]):
                type = BlockType.HEADING
            else:
                if lines[0] == '```':
                    if line_count >= 2 and lines[line_count-1].endswith('```'):
                        type = BlockType.CODE
                elif lines[0].startswith('>'):
                    type = BlockType.QUOTE
                    for line in lines[1:]:
                        if not line.startswith('>'):
                            type = BlockType.PARAGRAPH
                            break   
                elif lines[0].startswith('- '):
                    type = BlockType.UNORDERED_LIST
                    for line in lines[1:]:
                        if not line.startswith('- '):
                            type = BlockType.PARAGRAPH
                            break
                elif lines[0].startswith('1. '):
                    type = BlockType.ORDERED_LIST
                    for i in range(1, line_count):
                        if not lines[i].startswith(f'{i+1}. '):
                            type = BlockType.PARAGRAPH
                            break
    return type

def markdown_to_html_node(markdown):
    nodes = []
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.HEADING:
            nodes.append(process_heading(block))
        elif block_type == BlockType.CODE:
            nodes.append(process_code(block))
        elif block_type == BlockType.QUOTE:
            nodes.append(process_quote(block))
        elif block_type == BlockType.ORDERED_LIST:
            nodes.append(process_ordered_list(block))
        elif block_type == BlockType.UNORDERED_LIST:
            nodes.append(process_unordered_list(block))
        else:
            # Must be a paragraph 
            nodes.append(process_paragraph(block))
    return ParentNode('div', nodes)

def text_to_children(text):
    children = []
    text_nodes = text_to_textnodes(text)
    for text_node in text_nodes:
        children.append(text_node_to_html_node(text_node))
    return children

def process_heading(block):
    parts = block.split(sep=None, maxsplit=1)
    count = len(parts[0])
    tag = f'h{count}'
    text = parts[1]
    return ParentNode(tag, text_to_children(text))

def process_quote(block):
    lines = block.split('\n')
    children = []
    for line in lines:
        text = re.sub(r'^>\s*', '', line)
        nodes = text_to_children(text)
        if len(nodes) == 0:
            children.append(LeafNode('p', ''))
        else:
            children.extend(nodes)
    return ParentNode('blockquote', children)

def process_code(block):
    text = block[4:len(block)-3]
    return ParentNode('pre', [LeafNode('code', text)])

def process_ordered_list(block):
    lines = block.split('\n')
    children = []
    for line in lines:
        parts = re.findall(r"^(\d+. )(.*)", line)
        children.append(ParentNode('li', text_to_children(parts[0][1])))
    return ParentNode('ol', children)

def process_unordered_list(block):
    lines = block.split('\n')
    children = []
    for line in lines:
        parts = re.findall(r"^(- )(.*)", line)
        children.append(ParentNode('li', text_to_children(parts[0][1])))
    return ParentNode('ul', children)

def process_paragraph(block):
    return ParentNode('p', text_to_children(block.replace('\n', ' ')))

def extract_title(markdown):
    blocks = markdown_to_blocks(markdown)
    title = None
    for block in blocks:
        if block_to_block_type(block) == BlockType.HEADING:
            parts = block.split(sep=None, maxsplit=1)
            if len(parts[0]) == 1:
                title = parts[1]
                break
    
    if title == None:
        raise ValueError('No header found')
    
    return title

