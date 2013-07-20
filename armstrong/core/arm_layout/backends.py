from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


class BasicRenderModelBackend(object):
    def get_layout_template_name(self, model, name):
        ret = []
        for a in model.__class__.mro():
            if not hasattr(a, "_meta"):
                continue

            try:
                model_name = a._meta.model_name
            except AttributeError:  # DJANGO15 model_name is used in 1.6+
                model_name = a._meta.module_name

            ret.append("layout/%s/%s/%s.html" %
                (a._meta.app_label, model_name, name))
        return ret

    def render(self, object, name, dictionary=None,
            context_instance=None):
        dictionary = dictionary or {}
        dictionary["object"] = object
        template_name = self.get_layout_template_name(object, name)
        return mark_safe(render_to_string(template_name, dictionary=dictionary,
            context_instance=context_instance))

    def __call__(self, *args, **kwargs):
        return self.render(*args, **kwargs)
