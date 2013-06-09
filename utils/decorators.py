from functools import wraps
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import redirect

from .errors import StatusError
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
    if not settings.VERBOSE:
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

def html_view(func):
    @wraps(func)
    def funk(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except StatusError as e:
            return HttpResponse(str(e))
    return funk

def response_data(code=None, source=None, message=None, data={}):
     data['status'] = {'code': code, 'source': source, 'message': message}
     return data

def json_view(func):
    @wraps(func)
    def funk(*args, **kwargs):
        try:
            return JsonResponse(response_data('success', *func(*args, **kwargs)))
        except StatusError as e:
            return JsonResponse(response_data(**e.data()))
    return funk

def to_json(func):
    @wraps(func)
    def funk(*args, **kwargs):
        return JsonResponse(func(*args, **kwargs))
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


def require_key(field, key, message):
    def wrap(func):
        @wraps(func)
        def funk(request, *args, **kwargs):
            dic = getattr(request, field, None)
            if dic is None:
                raise StatusError('request', "No %s in request" % field)
            kwargs[key] = dic[key]
            '''
            try:
                kwargs[key] = dic[key]
            except KeyError, e:
                raise StatusError(key, e)
                raise StatusError('request', str(request)) raise StatusError('request', "%s missing in request.%s" % (key, field))
            '''
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


def renders_to(template=None):
    from django.shortcuts import render_to_response
    from django.template import RequestContext
    def wrap(func):
        @wraps(func)
        def funk(request, *args, **kwargs):
            data = func(request, *args, **kwargs)
            if isinstance(data, HttpResponse):
                return data
            elif data and 'template' in data:
                _template = data['template']
            else:
                _template = template
            return render_to_response(_template, data, RequestContext(request))
        return funk
    return wrap

def redirects_to(default=None):
    """
    Returns a reponse redirect to the function return value, else given
    default.
    """
    def decorator(func):
        @wraps(func)
        def funk(request, *args, **kwargs):
            data = func(request, *args, **kwargs)
            if data is None:
                return redirect(default)
            return redirect(data)
        return funk
    return decorator

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

def redirector(default='/'):
    """
    If decorated function returns a url, redirect to it.
    If decorated function returns None, use the 'next' GET paramater as
    redirect url if it is present, else redirect to the given default url.
    """
    def wrap(func):
        @wraps(func)
        def funk(request):
            ret = func(request)
            if ret is not None:
                return ret
            redirect_url = request.GET.get('next', default)
            return HttpResponseRedirect(redirect_url)
        return funk
    return wrap

