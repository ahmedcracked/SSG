class HTMLNode:
    def __init__(
        self,
        tag=None,
        value=None,
        children=None,
        props=None,
    ):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError("to_html method not implemented")

    def props_to_html(self):
        if self.props is None:
            return ""
        props_html = ""
        for prop, value in self.props.items():
            props_html += f' {prop}="{value}"'
        return props_html

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, children: {self.children}, {self.props})"


class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        if not self.tag:
            raise ValueError("All parent nodes must have a tag")
        if self.children is None:
            raise ValueError("All parent nodes must have children value")

        html_string = f"<{self.tag}{self.props_to_html()}>"
        for node in self.children:
            html_string += node.to_html()
        html_string += f"</{self.tag}>"

        return html_string

    def __repr__(self):
        return f"ParentNode({self.tag}, children: {self.children}, {self.props})"


class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        # this also raises error for empty strings because they're falsy
        if not self.value:
            raise ValueError("All leaf nodes must have a value")
        if self.tag is None:
            # return the HTMLNode as a raw string
            return self.value
        html_string = (
            f"<{self.tag}" + self.props_to_html() + f">{self.value}</{self.tag}>"
        )

        return html_string

    def __repr__(self):
        return f"LeafNode({self.tag}, {self.value}, {self.props})"
