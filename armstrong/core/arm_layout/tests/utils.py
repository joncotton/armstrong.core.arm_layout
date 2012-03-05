import random

from armstrong.dev.tests.utils.base import ArmstrongTestCase

from .arm_layout_support.models import Foobar, SubFoobar
from ..utils import get_layout_template_name


class get_layout_template_nameTestCase(ArmstrongTestCase):
    def setUp(self):
        super(get_layout_template_nameTestCase, self).setUp()
        self.m = Foobar()
        self.m2 = SubFoobar()
        self.name = "full_page"
        self._original_object_name = self.m._meta.object_name
        self._original_app_label = self.m._meta.app_label

    def tearDown(self):
        self.m._meta.object_name = self._original_object_name
        self.m._meta.app_label = self._original_app_label
        super(get_layout_template_nameTestCase, self).tearDown()

    def test_get_layout_template_name(self):
        """Test that the proper template path is returned"""

        result = get_layout_template_name(self.m, self.name)
        expected = 'layout/%s/%s/%s.html' % \
            (self.m._meta.app_label,
             self.m._meta.object_name.lower(),
             self.name)
        self.assertTrue(isinstance(result, list))  # assertIsInstance() new in Python 2.7
        self.assertEqual([expected], result)

        # okay if there isn't an actual file
        file_doesnt_exist = "fake_template"
        result = get_layout_template_name(self.m, file_doesnt_exist)
        expected = 'layout/%s/%s/%s.html' % \
            (self.m._meta.app_label,
             self.m._meta.object_name.lower(),
             file_doesnt_exist)
        self.assertEqual([expected], result)

        # requires an instance
        with self.assertRaises(TypeError):
            get_layout_template_name(type(self.m), self.name)

    def test_get_layout_template_random_app_name(self):
        """Test that the proper template path is returned"""

        self.m._meta.app_label = "random_%d" % random.randint(100, 200)
        result = get_layout_template_name(self.m, self.name)
        expected = 'layout/%s/foobar/%s.html' % \
            (self.m._meta.app_label, self.name)
        self.assertEqual([expected], result)

    def test_get_layout_template_random_model_name(self):
        """Test that the proper template path is returned"""

        self.m._meta.object_name = "random_%d" % random.randint(100, 200)
        result = get_layout_template_name(self.m, self.name)
        expected = 'layout/arm_layout_support/%s/%s.html' % \
            (self.m._meta.object_name, self.name)
        self.assertEqual([expected], result)

    def test_get_layout_template_random_tpl_name(self):
        """Test that the proper template path is returned"""

        name = "random_%d" % random.randint(100, 200)
        result = get_layout_template_name(self.m, name)
        expected = 'layout/arm_layout_support/foobar/%s.html' % name
        self.assertEqual([expected], result)

    def test_get_layout_template_inheritance(self):
        """
        Test that the proper order of templates in the
        Model inheritance structure is returned

        """
        result = get_layout_template_name(self.m2, self.name)
        expected_child = 'layout/%s/%s/%s.html' % \
            (self.m2._meta.app_label, self.m2._meta.object_name.lower(), self.name)
        expected_parent = 'layout/%s/%s/%s.html' % \
            (self.m._meta.app_label, self.m._meta.object_name.lower(), self.name)

        self.assertEqual([expected_child, expected_parent], result)
