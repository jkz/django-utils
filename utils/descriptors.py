def RenamedAttr(attr):
    class _RenamedAttr(object):
        def __get__(self, obj, cls=None):
            return getattr(obj, attr)
        def __set__(self, obj, val):
            return setattr(obj, attr, val)
        def __delete__(self, obj):
            return delattr(obj, attr)
    return _RenamedAttr()

class TempAttrClass(object):
    def __init__(self, *args, **kwargs):
        super(TempAttrClass, self).__init__(*args, **kwargs)
        for attr in dir(self):
            val = getattr(self, attr)
            if isinstance(val, TempAttr):
                val.deploy(attr, self)
                setattr(self, attr, CachedAttr

        

    def _cache(self, attr, val):
        setattr(self, '_'+attr, val)
    def _flush(self, attr):
        return getattr(self, '_'+attr, getattr(self, attr))
    def __getattr__(self):

class TempAttrBuilder(tuple):
    def deploy(self, obj, name):
        setattr(obj, name, TempAttr(self, attr)) for attr in self

class TempAttr(object):
    def __init__(self, name):
        self.name = name
    def ___get__(self, obj, cls=None):
        
