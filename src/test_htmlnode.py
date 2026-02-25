import unittest

from htmlnode import HTMLNode


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


if __name__ == "__main__":
    unittest.main()
