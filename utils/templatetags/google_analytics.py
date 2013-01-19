from django.conf import settings
from django import template

register = template.Library()

@register.simple_tag
def google_analytics():
    """
    Requires two settings:

    GOOGLE_ANALYTICS (bool)
    GOOGLE_SITE_ID (the site ID provided by google)

    If the settings are not present, this template tag will fail loudly.
    """
    if not settings.GOOGLE_ANALYTICS:
        return ''
    return (
"""
<script type="text/javascript">
  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', '%s']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();
</script>
""" % settings.GOOGLE_SITE_ID)
