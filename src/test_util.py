import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node
from textnode import TextNode, TextType
from util import BlockType, block_to_block_type, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, markdown_to_html_node, extract_title

class TestUtil(unittest.TestCase):
    def test_no_match(self):
        input = 'This is a test'
        output = split_nodes_delimiter([TextNode(input, TextType.TEXT)], '**', TextType.BOLD)

        self.assertEqual(output, [TextNode(input, TextType.TEXT)])

    def test_match_one(self):
        input = 'Text **bold** extra'
        output = split_nodes_delimiter([TextNode(input, TextType.TEXT)], '**', TextType.BOLD)
        expected = [
            TextNode('Text ', TextType.TEXT),
            TextNode('bold', TextType.BOLD),
            TextNode(' extra', TextType.TEXT)
        ]
        self.assertEqual(output, expected)

    def test_not_text(self):
        input = 'Test'
        output = split_nodes_delimiter([TextNode(input, TextType.BOLD)], '**', TextType.BOLD)
        self.assertEqual(output, [TextNode(input, TextType.BOLD)] )
    
    def test_mismatch(self):
        input = 'Test **foo'
        with self.assertRaises(ValueError):
            output = split_nodes_delimiter([TextNode(input, TextType.TEXT)], '**', TextType.BOLD)

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)
    
    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")], matches)

    def test_extract_mixed_markdown_images(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and an ![image](https://i.imgur.com/zjjcJKZ.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_mixed_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and an ![image](https://i.imgur.com/zjjcJKZ.png)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("to boot dev", "https://www.boot.dev")], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_link(self):
        node = TextNode(
            "This is text with an [link](https://i.imgur.com/zjjcJKZ.png) and another [second link](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second link", TextType.LINK, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )
    
    def test_split_link_and_image(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and a [link](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image(split_nodes_link([node]))
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and a ", TextType.TEXT),
                TextNode(
                    "link", TextType.LINK, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            text_to_textnodes(text)
        )

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_excess_lines_markdown_to_blocks(self):
        md = """
This is a **bolded** line

Next line.



Extra lines
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is a **bolded** line",
                "Next line.",
                "Extra lines"
            ]
        )


    def test_heading_block_type(self):
        text = '## Heading'
        self.assertEqual(BlockType.HEADING, block_to_block_type(text))

    def test_bad_heading_block_type(self):
        text = "#Heading"
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(text))

    def test_bad_heading_two_block_type(self):
        text = "foo# bar"
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(text))

    def test_code_block_type(self):
        text = """```
this is code
```"""
        self.assertEqual(BlockType.CODE, block_to_block_type(text))

    def test_not_code_block_type(self):
        text = """```
this is not code"""
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(text))

    def test_quote_block_type(self):
        text = ">quote"
        self.assertEqual(BlockType.QUOTE, block_to_block_type(text))

    def test_quote_lines_block_type(self):
        text = """>quote
> more quote"""
        self.assertEqual(BlockType.QUOTE, block_to_block_type(text))

    def test_quote_bad_quote_block_type(self):
        text = """>quote
not a quote"""
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(text))

    def test_unordered_list(self):
        text = """- Foo
- Bar"""
        self.assertEqual(BlockType.UNORDERED_LIST, block_to_block_type(text))

    def test_ordered_list(self):
        text = """1. Foo
2. Bar"""
        self.assertEqual(BlockType.ORDERED_LIST, block_to_block_type(text))

    def test_bad_unordered_list(self):
        text = """- Foo
Bar"""
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(text))

    def test_ordered_list(self):
        text = """1. Foo
3. Bar"""
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(text))

    def test_markdown_to_html_heading(self):
        md = '## Heading'
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><h2>Heading</h2></div>")

    def test_markdown_to_html_quote(self):
        md = """
>This is **bold**
>
> And more stuff
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html, 
            "<div><blockquote>This is <b>bold</b><p></p>And more stuff</blockquote></div>")

    def test_markdown_to_html_ol(self):
        md = """
1. First
2. _second_
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>First</li><li><i>second</i></li></ol></div>"
        )

    def test_markdown_to_html_ul(self):
        md = """
- First
- _second_
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>First</li><li><i>second</i></li></ul></div>"
        )

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_extract_title(self):
        md = "# Hello"
        title = extract_title(md)
        self.assertAlmostEqual(title, "Hello")

    def test_bad_extract_title(self):
        md = "## Not a title"
        with self.assertRaises(ValueError):
            extract_title(md)

if __name__ == "__main__":
    unittest.main()

