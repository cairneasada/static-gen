import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD, None)
        node2 = TextNode("This is a text node", TextType.BOLD, None)
        self.assertEqual(node, node2)

    def test_notEqualText(self):
        node = TextNode("This is a text node", TextType.BOLD, None)
        node2 = TextNode("This is a different text node", TextType.BOLD, None)
        self.assertNotEqual(node, node2)

    def test_notEqualTextType(self):
        node = TextNode("This is a text node", TextType.BOLD, None)
        node2 = TextNode(node.text, TextType.TEXT, node.url)
        self.assertNotEqual(node, node2)

    def test_notEqualUrl(self):
        node = TextNode("This is a text node", TextType.BOLD, None)
        node2 = TextNode(node.text, node.text_type, 'shttp://www.boot.dev')
        self.assertNotEqual(node, node2)

if __name__ == "__main__":
    unittest.main()