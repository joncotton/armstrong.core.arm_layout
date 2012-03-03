import re
import random

from django.template import Context, NodeList, Variable

from armstrong.dev.tests.utils.base import ArmstrongTestCase

from ..templatetags import layout_helpers
from .utils import generate_random_model


class RenderIterNodeTestCase(ArmstrongTestCase):

    def test_render_empty_block(self):
        node = layout_helpers.RenderIterNode(Variable('list'), NodeList())
        rendered = node.render(Context({'list': []}))
        self.assertEqual("", rendered)

    def test_render_non_iterable(self):
        model = generate_random_model()
        nodelist = NodeList()
        nodelist.append(layout_helpers.RenderNextNode("'full_page'"))
        node = layout_helpers.RenderIterNode(Variable("list"), nodelist)
        with self.assertRaises(TypeError):
            node.render(Context({"list": model}))

    def test_render_one_element(self):
        model = generate_random_model()
        nodelist = NodeList()
        nodelist.append(layout_helpers.RenderNextNode("'full_page'"))
        node = layout_helpers.RenderIterNode(Variable("list"), nodelist)
        rendered = node.render(Context({"list": [model]}))
        self.assertTrue(re.search(model.title, rendered))

    def test_render_multiple_elements(self):
        models = [generate_random_model() for i in range(random.randint(5, 8))]
        nodelist = NodeList()
        nodelist.append(layout_helpers.RenderNextNode("'full_page'"))
        nodelist.append(layout_helpers.RenderNextNode("'show_request'"))
        nodelist.append(layout_helpers.RenderNextNode("'full_page'"))
        node = layout_helpers.RenderIterNode(Variable("list"), nodelist)
        rendered = node.render(Context({"list": models}))
        self.assertTrue(re.search(models[0].title, rendered))
        self.assertFalse(re.search(models[1].title, rendered))
        self.assertTrue(re.search(models[2].title, rendered))
        self.assertFalse(re.search(models[3].title, rendered))

    def test_render_multiple_elements_with_extra_nexts(self):
        models = [generate_random_model() for i in range(2)]
        nodelist = NodeList()
        nodelist.append(layout_helpers.RenderNextNode("'full_page'"))
        nodelist.append(layout_helpers.RenderNextNode("'full_page'"))
        nodelist.append(layout_helpers.RenderNextNode("'show_request'"))
        nodelist.append(layout_helpers.RenderNextNode("'show_request'"))
        node = layout_helpers.RenderIterNode(Variable("list"), nodelist)
        rendered = node.render(Context({"list": models}))
        self.assertTrue(re.search(models[0].title, rendered))
        self.assertTrue(re.search(models[1].title, rendered))
        self.assertFalse(re.search('request', rendered))

    def test_render_multiple_elements_with_remainder(self):
        models = [generate_random_model() for i in range(random.randint(5, 8))]
        nodelist = NodeList()
        nodelist.append(layout_helpers.RenderNextNode("'full_page'"))
        nodelist.append(layout_helpers.RenderNextNode("'show_request'"))
        nodelist.append(layout_helpers.RenderNextNode("'full_page'"))
        nodelist.append(layout_helpers.RenderRemainderNode("'full_page'"))
        node = layout_helpers.RenderIterNode(Variable("list"), nodelist)
        rendered = node.render(Context({"list": models}))
        self.assertTrue(re.search(models[0].title, rendered))
        self.assertFalse(re.search(models[1].title, rendered))
        self.assertTrue(re.search(models[2].title, rendered))
        for model in models[3:]:
            self.assertTrue(re.search(model.title, rendered))
