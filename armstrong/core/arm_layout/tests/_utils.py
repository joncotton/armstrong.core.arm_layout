import random

from armstrong.dev.tests.utils.base import ArmstrongTestCase

from .arm_layout_support.models import Foobar


class TestCase(ArmstrongTestCase):
    pass


def generate_random_model():
    random_title = "This is a random title %d" % random.randint(1000, 2000)
    return Foobar(title=random_title)
