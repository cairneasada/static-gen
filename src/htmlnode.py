from textnode import TextNode, TextType

class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError
    
    def props_to_html(self):
        output = ''
        if self.props is not None and self.props:
            for key, value in self.props.items():
                output += f' {key}="{value}"'
        return output
    
    def __repr__(self):
        return f'{self.tag}; {self.value}; {self.children}; {self.props}'

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if self.value is None:
            raise ValueError('value is required')
        
        if self.tag is None:
            return self.value
        
        return f'<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>'
    
    def __repr__(self):
        return f'{self.tag}; {self.value}; s{self.props}'
    
class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        if self.tag is None:
            raise ValueError('tag is required')
        
        if self.children is None:
            raise ValueError("child list is required")
        
        return f'<{self.tag}>{self.child_html()}</{self.tag}>'
    
    def child_html(self):
        s = ''
        for i in self.children:
            s += i.to_html()
        return s
    
def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href": f'{text_node.url}'})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": f'{text_node.url}', "alt": f'{text_node.text}'})
    else:
        raise ValueError(f'Invalid text type: {text_node.text_type}')
