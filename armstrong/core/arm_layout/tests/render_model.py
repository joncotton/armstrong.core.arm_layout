import random
import fudge
from fudge.inspector import arg
from contextlib import contextmanager

from django.template import (Template, Context, RequestContext, Variable,
                             TemplateSyntaxError, VariableDoesNotExist)
from django.test.client import RequestFactory

from armstrong.dev.tests.utils.base import ArmstrongTestCase

from ..templatetags import layout_helpers
from .utils import generate_random_model


def contains_model(test_case, model):
    def test(value):
        test_case.assertTrue("object" in value, msg="sanity check")
        test_case.assertEqual(model, value["object"])
        return True
    return arg.passes_test(test)


class RenderObjectNodeTestCase(ArmstrongTestCase):
    def setUp(self):
        super(RenderObjectNodeTestCase, self).setUp()
        self.factory = RequestFactory()

    @contextmanager
    def stub_render_to_string(self):
        render_to_string = fudge.Fake().is_callable().returns("")
        with fudge.patched_context(layout_helpers, "render_to_string",
                render_to_string):
            yield

    @contextmanager
    def stub_get_layout_template_name(self):
        get_layout_template_name = fudge.Fake().is_callable().returns("")
        with fudge.patched_context(layout_helpers, "get_layout_template_name",
             get_layout_template_name):
            yield

    def test_dispatches_to_get_layout_template_name(self):
        model = generate_random_model()
        random_name = '"%d"' % random.randint(100, 200)
        node = layout_helpers.RenderObjectNode("object", random_name)

        fake = fudge.Fake()
        fake.is_callable().with_args(model, random_name).expects_call()
        with fudge.patched_context(layout_helpers, "get_layout_template_name", fake):
            with self.stub_render_to_string():
                node.render(Context({"object": model}))

        fudge.verify()

    def test_uses_the_name_provided_to_init_to_lookup_model(self):
        model = generate_random_model()
        random_object_name = "foo_%d" % random.randint(100, 200)
        node = layout_helpers.RenderObjectNode(random_object_name,
                "'full_name'")
        with self.stub_render_to_string():
            try:
                node.render(Context({random_object_name: model}))
            except VariableDoesNotExist:
                self.fail("should have found variable in context")

    def test_passes_request_into_context_if_available(self):
        model = generate_random_model()
        request = self.factory.get("/")
        node = layout_helpers.RenderObjectNode("object", "'show_request'")
        result = node.render(Context({"request": request, "object": model}))

        self.assertRegexpMatches(result, "WSGIRequest")

    def test_does_not_use_RequestContext_by_default(self):
        model = generate_random_model()
        node = layout_helpers.RenderObjectNode("object", "'debug'")
        with self.settings(DEBUG=False):
            result = node.render(Context({"object": model}))
            self.assertEqual(result.strip(), "debug: off")

    def test_uses_RequestContext_if_request_provided(self):
        model = generate_random_model()
        request = self.factory.get("/")
        node = layout_helpers.RenderObjectNode("object", "'debug'")

        with self.settings(DEBUG=True):
            context = RequestContext(request, {"object": model})
            result = node.render(context)
            self.assertEqual(result.strip(), "debug: on")

    def test_object_is_provided_to_context(self):
        model = generate_random_model()
        context = Context({"object": model})
        with self.stub_get_layout_template_name():
            render_to_string = fudge.Fake().is_callable().expects_call()
            render_to_string.with_args(arg.any(),
                    dictionary=contains_model(self, model),
                    context_instance=context)
            with fudge.patched_context(layout_helpers, "render_to_string",
                    render_to_string):
                node = layout_helpers.RenderObjectNode("object", "'foobar'")
                node.render(context)

    def test_can_pull_object_out_of_complex_context(self):
        model = generate_random_model()
        context = Context({"list": [model]})
        with self.stub_get_layout_template_name():
            render_to_string = fudge.Fake().is_callable().expects_call()
            render_to_string.with_args(arg.any(),
                    dictionary=contains_model(self, model),
                    context_instance=context)
            with fudge.patched_context(layout_helpers, "render_to_string",
                    render_to_string):
                node = layout_helpers.RenderObjectNode("list.0", "'foobar'")
                node.render(context)

    def test_original_context_is_not_contaminated(self):
        model = generate_random_model()
        obj = object()
        context = Context({"object": obj, "list": [model]})
        self.assertEqual(Variable("object").resolve(context), obj,
                msg="sanity check")
        with self.stub_render_to_string():
            node = layout_helpers.RenderObjectNode("list.0", "'foobar'")
            node.render(context)
        self.assertEqual(Variable("object").resolve(context), obj)


class render_modelTestCase(ArmstrongTestCase):
    def setUp(self):
        self.model = generate_random_model()
        self.string = """
            {% load layout_helpers %}{% render_model object "full_page" %}
        """.strip()

    @property
    def rendered_template(self):
        context = Context({"object": self.model})
        return Template(self.string).render(context)

    def test_dispatches_to_RenderObjectNode(self):
        self.assertRegexpMatches(self.rendered_template,
                "Title: %s" % self.model.title)

    def test_raises_intelligent_exception_on_error_too_many_parameters(self):
        self.string += "{% render_model object full_page one_to_many %}"
        with self.assertRaises(TemplateSyntaxError) as e:
            self.rendered_template
        expected = "Too many parameters"
        self.assertEqual(e.exception.message, expected)

    def test_raises_intelligent_exception_on_error_too_few_parameters(self):
        self.string += "{% render_model object %}"
        with self.assertRaises(TemplateSyntaxError) as e:
            self.rendered_template
        expected = "Too few parameters"
        self.assertEqual(e.exception.message, expected)

    def test_evaluates_variable_without_quotations(self):
        self.string += '{% render_model object layout_var %}'
        context = Context({"object": self.model, "layout_var": "full_page"})
        self.assertRegexpMatches(Template(self.string).render(context),
                "Title: %s" % self.model.title)

    def test_supports_single_quotes(self):
        self.string = self.string.replace('"', "'")
        self.assertRegexpMatches(self.rendered_template,
                "Title: %s" % self.model.title)
