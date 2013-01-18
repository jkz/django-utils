from django.conf import settings
from django.test import Client

settings.VERBOSE = True

c = Client()
