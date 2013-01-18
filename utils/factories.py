def model_manager_factory(model, filtered=True, **kwargs):
    from django.db.models import Manager
    class _Manager(Manager):
        def get_query_set(self):
           qs = super(model, self).get_query_set()
           return qs.filter(**kwargs) if filtered else qs.exclude(**kwargs)
    return _Manager

def obj_as_class(obj, new_cls, *args, **kwargs):
    """
    Return an object as a class instance.

    The returned object is an instance of the class but retains its old
    properties.
    """
    obj_typ = type(obj)
    if obj_typ is bool:
        # HURF DURF MY NAME IS PYTHON AND I CAN'T SUBCLASS bool.
        obj_typ = int

    class _Class(obj_typ, new_cls):
        __doc__ = new_cls.__doc__

        def __init__(self, obj, *args, **kwargs):
            obj_typ.__init__(self, obj)
            new_cls.__init__(self, *args, **kwargs)
        def __new__(cls, obj, *args, **kwargs):
            return obj_typ.__new__(cls, obj)


    return _Class(obj, *args, **kwargs)

class Shapeshifter(object):
    def morph(self, cls, *args, **kwargs):
        return obj_as_class(self, obj, *args, **kwargs)
