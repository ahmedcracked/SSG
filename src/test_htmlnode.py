import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_class_values(self):
        node = HTMLNode(
            "div",
            "I wish I could read",
        )
        self.assertEqual(
            node.tag,
            "div",
        )
        self.assertEqual(
            node.value,
            "I wish I could read",
        )
        self.assertEqual(
            node.children,
            None,
        )
        self.assertEqual(
            node.props,
            None,
        )

    def test_basic_to_html(self):
        node = HTMLNode(
            "div",
            "Hello, world!",
            None,
            {"class": "greeting", "href": "https://boot.dev"},
        )
        self.assertEqual(
            node.props_to_html(),
            ' class="greeting" href="https://boot.dev"',
        )

    def test_props_none_and_empty(self):
        n1 = HTMLNode(tag="p", value="x", props=None)
        self.assertEqual(n1.props_to_html(), "")

        n2 = HTMLNode(tag="p", value="x", props={})
        self.assertEqual(n2.props_to_html(), "")

    def test_props_boolean_handling(self):
        props = {"disabled": True, "hidden": False, "data": None}
        n = HTMLNode(tag="input", props=props)
        html = n.props_to_html()
        # Current implementation stringifies values, so True/False/None become "True"/"False"/"None"
        self.assertIn(' disabled="True"', html)
        self.assertIn(' hidden="False"', html)
        self.assertIn(' data="None"', html)

    def test_props_quoting_and_no_escaping(self):
        # The current implementation does not escape or sanitize values.
        val = 'a "quote" & more'
        n = HTMLNode(tag="span", props={"title": val})
        html = n.props_to_html()
        # Expect the raw value inside quotes (no escaping)
        self.assertIn(f' title="{val}"', html)

    def test_props_numeric_and_other_values(self):
        props = {"count": 123, "pi": 3.14}
        n = HTMLNode(tag="div", props=props)
        out = n.props_to_html()
        # Numeric values are stringified and placed in quotes
        self.assertIn(' count="123"', out)
        self.assertIn(' pi="3.14"', out)

    def test_props_order_and_multiple(self):
        props = {"a": 1, "b": 2, "c": 3}
        n = HTMLNode(tag="el", props=props)
        out = n.props_to_html()
        # All entries should be present (order preserved by dict insertion in CPython 3.7+)
        self.assertIn(' a="1"', out)
        self.assertIn(' b="2"', out)
        self.assertIn(' c="3"', out)

    def test_repr_basic(self):
        n = HTMLNode(tag="p", value="text", props={"class": "a"})
        r = repr(n)
        # The simple repr does not quote tag/value; they appear directly
        self.assertIn("HTMLNode(", r)
        self.assertIn("p, text", r)
        self.assertIn("children: None", r)
        self.assertIn("{'class': 'a'}", r)

    def test_repr_with_children(self):
        c1 = HTMLNode(tag="span", value="x", props={"class": "a"})
        c2 = HTMLNode(tag="img", value=None, props={"src": "1"})
        parent = HTMLNode(tag="div", children=[c1, c2], props={"id": "main"})
        r = repr(parent)
        # Parent repr includes children list (which uses the children's repr)
        self.assertIn("children:", r)
        self.assertIn("HTMLNode(", r)
        # Child tag/value pairs appear without quotes per current repr
        self.assertIn("span, x", r)
        self.assertIn("img, None", r)

    def test_raw_node_repr(self):
        raw = HTMLNode(value="raw & text")
        r = repr(raw)
        # Tag is None and value appears directly in the repr
        self.assertTrue(r.startswith("HTMLNode("))
        self.assertIn("None, raw & text", r)


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_empty_value_raises(self):
        node = LeafNode("p", "")
        with self.assertRaises(ValueError):
            node.to_html()

    def test_leaf_none_value_raises(self):
        node = LeafNode("p", "temp")
        node.value = None  # to make the static typer ignore the typing error
        with self.assertRaises(ValueError):
            node.to_html()

    def test_leaf_tag_none_returns_raw(self):
        node = LeafNode(None, "raw output")
        self.assertEqual(node.to_html(), "raw output")

    def test_leaf_props_included(self):
        node = LeafNode("a", "link", {"href": "https://example.com"})
        self.assertEqual(node.to_html(), '<a href="https://example.com">link</a>')

    def test_leaf_props_boolean_and_none(self):
        props = {"disabled": True, "hidden": False, "data": None}
        node = LeafNode("input", "value", props)
        out = node.to_html()
        # Current props behavior stringifies all values into attributes
        self.assertIn(' disabled="True"', out)
        self.assertIn(' hidden="False"', out)
        self.assertIn(' data="None"', out)

    def test_leaf_repr(self):
        node = LeafNode("p", "text", {"class": "a"})
        self.assertEqual(repr(node), "LeafNode(p, text, {'class': 'a'})")


class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_parent_tag_none_raises(self):
        child_node = LeafNode("span", "child")
        with self.assertRaises(ValueError):
            ParentNode(None, [child_node]).to_html()

    def test_parent_children_none_raises(self):
        with self.assertRaises(ValueError):
            ParentNode("div", None).to_html()

    def test_parent_props_included_in_to_html(self):
        # ParentNode.to_html should include props on the opening tag via props_to_html()
        parent_node = ParentNode("div", [], {"id": "main"})
        self.assertEqual(parent_node.to_html(), '<div id="main"></div>')

    def test_parent_with_empty_children_renders_empty_tags(self):
        parent_node = ParentNode("section", [])
        self.assertEqual(parent_node.to_html(), "<section></section>")

    def test_parent_with_mixed_children_includes_raw_and_leaf(self):
        # Ensure raw (tag=None) children are included verbatim alongside normal children
        leaf_node = LeafNode("span", "c")
        raw_node = LeafNode(None, "raw")
        parent_node = ParentNode("div", [leaf_node, raw_node])
        self.assertEqual(parent_node.to_html(), "<div><span>c</span>raw</div>")

    def test_parent_props_boolean_and_none_are_stringified(self):
        # props_to_html stringifies values; ensure that behavior is preserved for ParentNode
        props = {"disabled": True, "hidden": False, "data": None}
        parent_node = ParentNode("div", [], props)
        out = parent_node.to_html()
        self.assertIn(' disabled="True"', out)
        self.assertIn(' hidden="False"', out)
        self.assertIn(' data="None"', out)
        # Basic sanity: output begins with opening tag
        self.assertTrue(out.startswith("<div "))

    def test_nested_parent_props_and_children(self):
        # Nested ParentNodes should render both tags and their props
        grandchild_node = LeafNode("i", "x")
        child_node = ParentNode("span", [grandchild_node], {"class": "c"})
        parent_node = ParentNode("div", [child_node], {"id": "main"})
        self.assertEqual(
            parent_node.to_html(),
            '<div id="main"><span class="c"><i>x</i></span></div>',
        )

    def test_non_htmlnode_child_raises_attribute_error(self):
        # If a child isn't an HTMLNode (and thus has no to_html), an AttributeError will occur
        parent_node = ParentNode("div", ["not-a-node"])
        with self.assertRaises(AttributeError):
            parent_node.to_html()


if __name__ == "__main__":
    unittest.main()
