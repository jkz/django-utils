import datetime
import string

from django.utils.http import urlencode

def url_append_querystring(url, query):
    return '%s?%s' % (url, urlencode(query))

def unique_name(i, prefix, s="", a=string.uppercase):
    if i >= 0:
	return unique_name(i - 26, s + a[i % 26], string.lowercase)
    else:
	return '%s %s' % s

def to_tuple(obj):
    if isinstance(obj, (list, tuple)):
        return obj
    else:
        return obj,

def haskey(obj, key):
    try:
        return key in obj
    except TypeError:
        return False

def attr_as(name):
    """Create a property on a class that is another attribute"""
    @property
    def _attr(self):
        return getattr(self, name)
    return _attr

def subdict(obj, *names):
    return dict((name, getattr(obj, name)) for name in names)

def handler(signal, sender):
    def _decorator(func):
        signal.connect(func,
                       sender=sender,
                       weak=False,
                       dispatch_uid=func.__name__)
        return func
    return _decorator

def is_cooldowned(timestamp, seconds):
    return datetime.datetime.now() - timestamp > datetime.timedelta(seconds=seconds)

#TODO is this 1 second off?
def is_cooldowning(timestamp, seconds):
    return not is_cooldowned(timestamp, seconds)


def import_module(path):
    return reduce(getattr, path.split('.')[1:], __import__(path))

def dir_module_public(path):
    return filter(lambda x: x[0] != '_', dir(import_module(path)))

def list_modules(path):
    import pkgutil
    return [name for importer, name, ispkg in pkgutil.iter_modules(path)]

def list_modules(package):
    import pkgutil
    prefix = package.__name__ + '.'
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix):
        __import__(modname, fromlist="dummy")
