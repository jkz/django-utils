import functools
from datetime import datetime

from django.db import models as m

DefaultTextField = functools.partial(m.TextField, default='', blank=True)
NullTextField = functools.partial(m.TextField, blank=True, null=True)
DefaultBooleanField = functools.partial(m.BooleanField, default=False)
DefaultIntegerField = functools.partial(m.IntegerField, default=0)

class CastToTextField(m.TextField):
    __metaclass__ = m.SubfieldBase
    def __init__(self, cast=lambda x: x, **kwargs):
        super(CastToTextField, self).__init__(**kwargs)
        self.cast = cast

    def get_prep_value(self, value):
        return self.cast(value)

    def to_python(self, value):
        return self.cast(value)


class TimestampField(m.DateTimeField):
    def __init__(self, default=datetime.now, **kwargs):
        super(TimestampField, self).__init__(default=default, **kwargs)
    '''
    def pre_save(self, model_instance, add):
        if add and not getattr(model_instance, self.attname):
            setattr(model_instance, self.attname, datetime.now())
        return getattr(model_instance, self.attname)
    '''

