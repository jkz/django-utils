import callm

from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def twitter_share(context, url=None, text='', via=None):
    query = {}
    if url:
        query['url'] = url
    else:
        query['url'] = context['request'].build_absolute_url()
    if text:
        query['text'] = text
    if via:
        query['via'] = via
    return callm.URL('https://twitter.com/intent/tweet', query=query, verbatim=True)

@register.simple_tag(takes_context=True)
def facebook_share(context, url=None, title=None, summary=None, images=None):
    query = {}
    if url:
        query['p[url]'] = url
    else:
        query['p[url]'] = context['request'].build_absolute_url()
    if title:
        query['p[title]'] = title
    if summary:
        query['p[summary]'] = title
    if images:
        if isinstance(images, basestring):
            images = [images]
        for idx, image in enumerate(images):
            query['p[images][%s]' % idx] = image
    return callm.URL('http://www.facebook.com/sharer/sharer.php', query=query, verbatim=True)

@register.simple_tag(takes_context=True)
def googleplus_share(context, url=None):
    query = {}
    if url:
        query['url'] = url
    else:
        query['url'] = context['request'].build_absolute_url()
    return callm.URL('https://plus.google.com/share', query=query)

@register.simple_tag(takes_context=True)
def pinterest_share(context, media, url=None, description=None):
    query = {'media': media}
    if url:
        query['url'] = url
    else:
        query['url'] = context['request'].build_absolute_url()
    if description:
        query['description'] = description
    return callm.URL('http://pinterest.com/pin/create/button/', query=query)


@register.simple_tag(takes_context=True)
def tumblr_photo(context, source, url=None, caption=None):
    query = {'source': source}
    if url:
        query['clickthru'] = url
    else:
        query['clickthru'] = context['request'].build_absolute_url()
    if caption:
        query['caption'] = caption
    return callm.URL('http://www.tumblr.com/share/photo', query=query)
