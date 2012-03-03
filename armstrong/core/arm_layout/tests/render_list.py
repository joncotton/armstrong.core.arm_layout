import re
import fudge
import random
from contextlib import contextmanager

from django.template import Template, Context, Variable, VariableDoesNotExist

from armstrong.dev.tests.utils.base import ArmstrongTestCase

from ..templatetags import layout_helpers
from .utils import generate_random_model


class RenderListNodeTestCase(ArmstrongTestCase):

    @contextmanager
    def stub_render_to_string(self):
        render_to_string = fudge.Fake().is_callable().returns("")
        with fudge.patched_context(layout_helpers, "render_to_string",
                render_to_string):
            yield

    def test_variable_resolution_for_list(self):
        random_list_name = "list_%d" % random.randint(100, 200)
        rln = layout_helpers.RenderListNode(
                    Variable(random_list_name),
                    "'debug'")
        with self.stub_render_to_string():
            try:
                rln.render(Context({random_list_name: [generate_random_model()]}))
            except VariableDoesNotExist:
                self.fail("should have found variable in context")
        fudge.verify()

    def test_variable_resolution_for_name(self):
        random_name_name = "name_%d" % random.randint(100, 200)
        rln = layout_helpers.RenderListNode(
                    Variable('list'),
                    random_name_name)
        with self.stub_render_to_string():
            try:
                rln.render(Context({'list': [generate_random_model()],
                                    random_name_name: 'debug'}))
            except VariableDoesNotExist:
                self.fail("should have found variable in context")
        fudge.verify()

    def test_finds_new_templates_for_each_model(self):
        rln = layout_helpers.RenderListNode(
                    Variable('list'),
                    "'debug'")
        num_models = random.randint(5, 10)
        with self.stub_render_to_string():
            try:
                rln.render(Context({'list': [generate_random_model()
                    for i in range(num_models)]}))
            except VariableDoesNotExist:
                self.fail("should have found variable in context")
        fudge.verify()


class render_listTestCase(ArmstrongTestCase):

    def test_filters_list_argument(self):
        string = """
            {% load layout_helpers %}{% render_list list|slice:":3" "full_page" %}
        """.strip()
        model_list = [generate_random_model()
                        for i in range(random.randint(5, 10))]
        context = Context({"list": model_list})
        rendered = Template(string).render(context)

        self.assertEqual(3, len(re.findall('Full Page', rendered)))
        self.assertTrue(re.search('Title: %s' % model_list[0].title, rendered))
        self.assertTrue(re.search('Title: %s' % model_list[1].title, rendered))
        self.assertTrue(re.search('Title: %s' % model_list[2].title, rendered))
        self.assertFalse(re.search('Title: %s' % model_list[3].title, rendered))
