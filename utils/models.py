from django.db import models as m
from django.db.models.query import QuerySet

class PolyModel:
    def proxy(self, proxy_cls):
        proxy_obj = proxy_cls()
        proxy_obj.__dict__ = self.__dict__
        return proxy_obj

class FilterManager(m.Manager):
    def __init__(self, *args, **kwargs):
        super(FilterManager, self).__init__()
        self.args = args
        self.kwargs = kwargs

    def get_query_set(self):
        return super(FilterManager, self).get_query_set() \
                .filter(*self.args, **self.kwargs)


class QuerySetManager(m.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return getattr(self.model, 'QuerySet', QuerySet)(model=self.model,
                using=self._db)

    def __getattr__(self, attr, *args):
        if attr.startswith("_"): # or at least "__"
            raise AttributeError
        return getattr(self.get_query_set(), attr, *args)


class QuerySetModel(m.Model):
    objects = QuerySetManager()

    class Meta:
        abstract = True

    class QuerySet(QuerySet):
        pass


from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
class VerifyUniqueMixin:
    # There is a validate unique method on classes already
    def x_verify_unique(self, query=lambda x: None):
        try:
            other = query()
        except ObjectDoesNotExist:
            pass
        except MultipleObjectsReturned:
            #TODO: warn admin
            raise IntegrityError("Invalid state, unique constraint %s" % str(self))
        else:
            if other is not None and self.pk != other.pk:
                raise IntegrityError("Unique constraint violated %s" % str(self))

class MapFilterMixin:
    def map_filter(self, template='%s', callback=lambda x: x, **kwargs):
        """
        Map a callback function on each value of the kwargs dict. Replace the
        keys by inserting them in a template. Finally filter with the new
        key, value pairs as arguments.
        """
        return self.filter(**dict((template % key, callback(val))
                for key, val in kwargs.items()))

class PaginatorMixin:
    def paginate(self, limit=10, offset=0):
        return self.all()[offset:offset + limit]

class TimestampMixin(MapFilterMixin):
    def _to_timestamp(self, obj):
        from datetime import datetime
        if isinstance(obj, datetime):
            return obj

        #XXX decide on parsing methods
        try:
            return datetime.strptime(obj, 'format')
        except ValueError:
            pass

        try:
            return self.model.objects.get(pk=obj).timestamp
        except (self.model.DoesNotExist, TypeError): # Verify if this is throwed
            return obj

    def before(self, **kwargs):
        return self.map_filter('%s__lt', **kwargs)

    def after(self, **kwargs):
        return self.map_filter('%s__gt', **kwargs)

    def ubefore(self, **kwargs):
        return self.map_filter('%s__lt', **kwargs)

    def uafter(self, **kwargs):
        return self.map_filter('%s__gt', **kwargs)


class RequestQuerySet(m.query.QuerySet, PaginatorMixin, TimestampMixin):
    def request(self, req=None, **kwargs):
        """Intended for return pages of requests"""
        #XXX THIS IS FUGLY
        if req:
            offset = req.GET.get('offset', 0)
            limit = req.GET.get('limit', 10)
            ubefore = req.GET.get('ubefore', None)
            if not ubefore:
                before = req.GET.get('before', None)

            uafter = req.GET.get('uafter', None)
            if not uafter:
                after = req.GET.get('after', None)
        else:
            offset = 0
            limit = 10
            before = None
            after = None

        offset = kwargs.pop('offset', offset)
        limit = kwargs.pop('limit', limit)

        ubefore = kwargs.pop('ubefore', ubefore)
        if not ubefore:
            kwargs.pop('ubefore', before)

        uafter = kwargs.pop('uafter', uafter)
        if not ubefore:
            after = kwargs.pop('after', after)

        qs = self.filter(**kwargs)

        # Set the timescope
        if ubefore is not None:
            qs = qs.ubefore(timestamp=ubefore)
        elif before is not None:
            qs = qs.before(pk=before)

        if uafter is not None:
            qs = qs.uafter(timestamp=uafter)
        elif after is not None:
            qs = qs.after(pk=after)

        # Paginate the request
        pagination = {}
        if offset is not None:
            pagination['offset'] = int(offset)
        if limit is not None:
            pagination['limit'] = int(limit)

        return qs.paginate(**pagination)


class ExternalManager(m.Manager):
    def put(self, **data):
        # Handle non-relational fields
        #XXX: stuff like timestamp conversion should be taken care of by
        #     a validation function
        fields = dict((key, val) for key, val in data.items()
                if key in (field.name for field in self.model._meta.fields if
                    type(field) != m.fields.related.ForeignKey))
        obj = self.model(**fields)

        # Handle relational fields
        #XXX: only foreign keys at the moment
        for name in (field.name for field in self.model._meta.fields if
                type(field) == m.fields.related.ForeignKey):
            try:
                setattr(obj, name, data[name])
            except KeyError:
                try:
                    name = name + '_id'
                    setattr(obj, name, data[name])
                except KeyError:
                    pass

        obj.save()
        return obj


class ExternalModel(m.Model):
    objects = m.Manager()
    importer = ExternalManager()

    class Meta:
        abstract = True

