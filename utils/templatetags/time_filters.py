from django import template

from ..times import fuzzy_time

register = template.Library()

register.filter('fuzzy_time', fuzzy_time)

