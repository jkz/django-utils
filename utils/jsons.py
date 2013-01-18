import json

from django.http import HttpResponse

JSON_CONTENT_TYPE = 'json'

def obj2json(obj, indent=2):
    def handler(_obj):
        if hasattr(_obj, 'isoformat'):
            return _obj.isoformat()
        else:
            raise TypeError('%s %s is not jsonserializable' 
                    % (type(_obj), str(_obj)))
    return json.dumps(obj, indent=2, default=handler)

#TODO proper error handling
class JsonResponse(HttpResponse):
    content_type = JSON_CONTENT_TYPE

    def __init__(self, obj, **kw):
        super(JsonResponse, self).__init__(obj2json(obj), mimetype='application/json', **kw)
