from functools import wraps
from .jsons import JsonResponse

def to_template(template=None):
    from django.shortcuts import render_to_response
    from django.template import RequestContext
    def wrap(func):
        @wraps(func)
        def funk(request, *args, **kwargs):
            data = func(request, *args, **kwargs)
            if data:
                _template = data.pop('template', template)
            else:
                _template = template
            return render_to_response(_template, data, RequestContext(request))
        return funk
    return wrap

def to_json(func):
    @wraps(func)
    def funk(*args, **kwargs):
        return JsonResponse(func(*args, **kwargs))
    return funk

