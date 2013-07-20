import random
import django
import fudge

from .arm_layout_support.models import Foobar, SubFoobar
from ..utils import get_layout_template_name
from ._utils import TestCase


class get_layout_template_nameTestCase(TestCase):
    def setUp(self):
        super(get_layout_template_nameTestCase, self).setUp()
        self.m = Foobar()
        self.m2 = SubFoobar()
        self.name = "full_page"
        self._original_model_name = self.m._meta.model_name
        self._original_app_label = self.m._meta.app_label

    def tearDown(self):
        self.m._meta.model_name = self._original_model_name
        self.m._meta.app_label = self._original_app_label
        super(get_layout_template_nameTestCase, self).tearDown()

    def test_requires_a_model_instance(self):
        with self.assertRaises(TypeError):
            get_layout_template_name(type(self.m), self.name)

    def test_returns_proper_path(self):
        result = get_layout_template_name(self.m, self.name)
        expected = 'layout/%s/%s/%s.html' % \
            (self.m._meta.app_label,
             self.m._meta.model_name,
             self.name)
        self.assertEqual([expected], result)

    def test_missing_file_is_okay(self):
        file_doesnt_exist = "fake_template"
        result = get_layout_template_name(self.m, file_doesnt_exist)
        expected = 'layout/%s/%s/%s.html' % \
            (self.m._meta.app_label,
             self.m._meta.model_name,
             file_doesnt_exist)
        self.assertEqual([expected], result)

    def test_uses_app_label_in_template_name(self):
        self.m._meta.app_label = "random_%d" % random.randint(100, 200)
        result = get_layout_template_name(self.m, self.name)
        expected = 'layout/%s/foobar/%s.html' % \
            (self.m._meta.app_label, self.name)
        self.assertEqual([expected], result)

    def test_uses_model_name_in_template_name(self):
        self.m._meta.model_name = "random_%d" % random.randint(100, 200)
        result = get_layout_template_name(self.m, self.name)
        expected = 'layout/arm_layout_support/%s/%s.html' % \
            (self.m._meta.model_name, self.name)
        self.assertEqual([expected], result)

    def test_uses_name_in_template_name(self):
        name = "random_%d" % random.randint(100, 200)
        result = get_layout_template_name(self.m, name)
        expected = 'layout/arm_layout_support/foobar/%s.html' % name
        self.assertEqual([expected], result)

    def test_can_find_templates_through_models_inheritance(self):
        """
        Test that the proper order of templates in the
        Model inheritance structure is returned

        """
        result = get_layout_template_name(self.m2, self.name)
        expected_child = 'layout/%s/%s/%s.html' % \
            (self.m2._meta.app_label, self.m2._meta.model_name, self.name)
        expected_parent = 'layout/%s/%s/%s.html' % \
            (self.m._meta.app_label, self.m._meta.model_name, self.name)

        self.assertEqual([expected_child, expected_parent], result)

    def test_meta_model_name_is_used(self):
        class ModelFake(fudge.Fake):
            _meta = fudge.Fake().has_attr(
                app_label="fakeapplabel",
                model_name="fakemodelname")

        fake_model = ModelFake()
        result = get_layout_template_name(fake_model, self.name)
        expected = 'layout/fakeapplabel/fakemodelname/%s.html' % self.name
        self.assertEqual([expected], result)

    if django.VERSION < (1, 6):  # DJANGO15 drop this when we drop Django 1.5 support
        def test_meta_module_name_is_used_pre_django16(self):
            class ModelFake(fudge.Fake):
                _meta = fudge.Fake().has_attr(
                    app_label="fakeapplabel",
                    module_name="fakemodelname")

            fake_model = ModelFake()
            with self.assertRaises(AttributeError):
                fake_model._meta.model_name

            result = get_layout_template_name(fake_model, self.name)
            expected = 'layout/fakeapplabel/fakemodelname/%s.html' % self.name
            self.assertEqual([expected], result)
