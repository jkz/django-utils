"""
Plucked from http://djangosnippets.org/snippets/2615/
"""


from django.core.cache import cache
from django.db import models

#Inspiration snippet:
#
#(I was thinking of using this at the end, but the issues of nesting
#these are not worth the headache)
#
#class cached_property(object):
#    '''
#    A read-only @property that is only evaluated once per python object. The value
#    is cached on the object itself rather than the function or class; this should prevent
#    memory leakage.
#
#    Model instances are re-instantiated for each request, so this should be the last line
#    of defense in a django context.
#    '''
#    def __init__(self, fget, doc=None):
#        self.fget = fget
#        self.__doc__ = doc or fget.__doc__
#        self.__name__ = fget.__name__
#        self.__module__ = fget.__module__
#
#    def __get__(self, obj, cls):
#        if obj is None:
#            return self
#        obj.__dict__[self.__name__] = result = self.fget(obj)
#        return result

class cached_model_property(object):
    """
    To use inside the class declaration for SomeClass
    1. First make a subclass of of this:

    class cached_someclass_property(cached_model_property):
        model_name = "SomeClass"

    2. Use as if this were a @property decorator inside SomeClass

    This should of course only be used if the property is essentially
    static. If the property should return a given model instance, where
    the instance id is static but the contents could change, see gives_a
    decorator below.
    """
    model_name = "<generic>"

    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__

    @staticmethod
    def pickle(cuke):
        """Pickling/unpickling is used before saving to the django (outermost) cache."""
        return cuke

    @staticmethod
    def unpickle(dill):
        return dill

    def __get__(self, obj, cls):
        """Use the descriptor protocol to act as a property.

        3 levels of caching implemented:
        outermost: django cache
        middle: obj._cache (for multiple properties on a single object)
        innermost: replace the attribute on this object, so we can entirely avoid
            running this function a second time.
        """

        #First, handle the "unbound" case
        if obj is None:
            return self

        key = ':'.join((self.model_name, str(obj.id)))

        try:
            #middle cache pull
            obj_cache = obj._cache
        except AttributeError:
            #outermost cache pull
            obj_cache = cache.get(key)
            if obj_cache is None:
                obj_cache = {}
                #cache.set(key, {}) #technically, this might improve multithreaded performance, but not worth it.
            #middle cache push
            #since this is a mutable reference, further changes below will apply
            obj._cache = obj_cache

        #unpack property from dict of all cached properties for this object
        try:
            result = self.unpickle(obj_cache[self.__name__])
        except:
            #missing - calculate value and add to cache
            result = self.fget(obj)
            obj_cache[self.__name__] = self.pickle(result)
            #outermost cache push
            cache.set(key, obj_cache)

        #innermost cache push (no pull because this function itself is replaced)
        obj.__dict__[self.__name__] = result = self.fget(obj)

        #return
        return result

MODELS = {}
class cached_typed_model_property(cached_model_property):
    @staticmethod
    def pickle(cuke):
        if isinstance(cuke, models.Model):
            cls = cuke.__class__
            name = cls.__name__
            MODELS[name] = cls
            return (name, cuke.id)
        try:
            if issubclass(cuke, models.Model):
                name = cuke.__name__
                MODELS[name] = cuke
                return (name,)
        except TypeError: #issubclass is annoying that way
            pass
        return cuke #for None

    @staticmethod
    def unpickle(dill):
        if isinstance(dill, tuple):
            if len(dill) == 2:
                return MODELS[dill[0]].objects.get(id=dill[1])
                #exceptions here just mean we run the function again, which will end up adding the model to MODELS
            if len(dill) == 1:
                return MODELS[dill[0]]
        return dill

class cached_uprop(cached_typed_model_property):
    model_name = "Users"
