import django
from django.db import models


class Foobar(models.Model):
    title = models.CharField(max_length=100)

    # DJANGO15 drop this when we drop Django 1.5 support
    if django.VERSION < (1, 6):
        def __init__(self, *args, **kwargs):
            super(Foobar, self).__init__(*args, **kwargs)
            self._meta.model_name = self._meta.module_name


class SubFoobar(Foobar):
    pass
