import json

from django import template

register = template.Library()

register.filter('json_dumps', json.dumps)

