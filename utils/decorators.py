from functools import wraps
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import redirect

from .jsons import JsonResponse

def model__getattr__(func):
    """
    This decorator should allow a custom __getattr__ method for model
    classes.
    """
    #XXX: Doesn't work yet, complicated.
    def __getattr__(self, name):
        try:
            return super(self.__class__, self).__getattribute__(name)
        except AttributeError:
            if name.startswith('_prefetched'):
                raise
        try:
            return getattr(self._meta, name)
        except AttributeError:
            pass
        return func(self, name)
    return __getattr__


# Holds the indent level as a string of spaces
__ = ''
def shoutout(func):
    """
    Prints the function name, passed arguments and return value when VERBOSE
    setting is true.
    """
    if not getattr(settings, 'VERBOSE'):
        return func
    @wraps(func)
    def _func(*args, **kwargs):
        global __
        def _p(s):
            print(__ + str(s))
        _p('%s.%s(' % (func.__module__, func.__name__))
        for arg in args:
            _p('  %s' % str(arg))
        for key, val in kwargs.iteritems():
            _p('  %s=%s' % (str(key), str(val)))
        _p(')')
        __ += '    '
        try:
            ret = func(*args, **kwargs)
        except Exception as e:
            _p(e)
            raise e
        __ = __[:-4]
        _p('return %s.%s: %s' % (func.__module__, func.__name__, ret))
        return ret
    return _func

def to_text(func):
    """
    Wraps decorated function's return value in an HttpResponse
    """
    @wraps(func)
    def funk(*args, **kwargs):
        response = func(*args, **kwargs)
        if isinstance(response, HttpResponse):
            return response
        return HttpResponse(response)
    return funk

def to_json(func):
    """
    Wrap decorated function's return value in a JsonResponse
    """
    @wraps(func)
    def funk(*args, **kwargs):
        response = func(*args, **kwargs)
        if isinstance(response, HttpResponse):
            return response
        return JsonResponse(response)
    return funk

def receiver(*args, **kwargs):
    """
    A wrapper around the native receiver decorator, providing a unique
    dispatch_uid and sets weak=False.
    """
    def wrap(func):
        from django import dispatch
        return dispatch.receiver(
            *args,
            weak=kwargs.pop('weak', False),
            dispatch_uid=kwargs.pop('dispatch_uid', '%s.%s' % (func.__module__, func.__name__)),
            **kwargs)(func)
    return wrap

def created_receiver(model, **kwargs):
    """
    Connect to a post_save_signal only if an object was created
    """
    def wrap(func):
        from django.db.models.signals import post_save
        @wraps(func)
        @receiver(post_save, sender=model)
        def funk(*args, **named):
            if named.pop('created', False):
                return func(*args, **named)
    return wrap


def require_key(container, key, message):
    """
    Require a key from a container on the request object and pass it as
    a keyword argument to the decorated function.
    """
    def wrap(func):
        @wraps(func)
        def funk(request, *args, **kwargs):
            kwargs[key] = getattr(request, container)[key]
            return func(request, *args, **kwargs)
        return funk
    return wrap

def require_meta(*a, **kw):
    return require_key('META', *a, **kw)
def require_get(*a, **kw):
    return require_key('GET', *a, **kw)
def require_post(*a, **kw):
    return require_key('POST', *a, **kw)
def require_request(*a, **kw):
    return require_key('REQUEST', *a, **kw)
def require_session(*a, **kw):
    return require_key('session', *a, **kw)


def default_key(field, key, default=None):
    """
    Provide a key from a container on the request object and pass it as a
    keyword argument to decorated function. If the key is missing, pass the
    default value in stead.
    """
    def wrap(func):
        @wraps(func)
        def funk(request, *args, **kwargs):
            kwargs[key] = getattr(request, field, {}).get(key, default)
            return func(request, *args, **kwargs)
        return funk
    return wrap

def default_meta(*a, **kw):
    return require_key('META', *a, **kw)
def default_get(*a, **kw):
    return require_key('GET', *a, **kw)
def default_post(*a, **kw):
    return require_key('POST', *a, **kw)
def default_request(*a, **kw):
    return require_key('REQUEST', *a, **kw)
def default_session(*a, **kw):
    return require_key('session', *a, **kw)



def renders_to(template=None):
    """
    The return dictionary from the decorated function is passed to the
    given template as context, together with the default request context.
    When function returns a HttpResponse, that response is returned in stead.
    When function returns two arguments, the second is the template.
    """
    from django.shortcuts import render_to_response
    from django.template import RequestContext
    def wrap(func):
        @wraps(func)
        def funk(request, *args, **kwargs):
            data = func(request, *args, **kwargs)

            if isinstance(data, HttpResponse):
                return data
            if not hasattr(data, 'get'):
                try:
                    data, _template = data
                except TypeError:
                    _template = template
            return render_to_response(_template, data, RequestContext(request))
        return funk
    return wrap

def default_kwargs(**defaults):
    def wrap(func):
        @wraps(func)
        def funk(*args, **kwargs):
            # Copy the defaults so they don't get messed up in place
            _kwargs = defaults.copy()
            _kwargs.update(kwargs)
            return func(*args, **_kwargs)
        return funk
    return wrap


# The following two decorators are very similar,
# probably one should get the shaft.

def redirects_to(default=None):
    """
    Returns a (redirect) response based on decorated function's return value.
    When decorated function returns:
    - a HttpResponse, return it in stead of the redirect
    - a value, redirect to it
    - None, redirect to given default
    """
    def decorator(func):
        @wraps(func)
        def funk(request, *args, **kwargs):
            response = func(request, *args, **kwargs)
            if isinstance(response, HttpResponse):
                return response
            elif response is None:
                return redirect(default)
            return redirect(response)
        return funk
    return decorator


def redirector(default='/'):
    """
    Returns a (redirect) response based on decorated function's return value.
    When decorated function returns:
    - a HttpRequest, return it in stead
    - a url, redirect to it
    - None and GET has a 'next', redirect to that
    else redirect to the given default url
    """
    def wrap(func):
        @wraps(func)
        def funk(request):
            response = func(request)
            if isinstance(response, HttpResponse):
                return response
            elif response is not None:
                redirect_url = response
            else
                redirect_url = request.GET.get('next', default)
            return HttpResponseRedirect(redirect_url)
        return funk
    return wrap

