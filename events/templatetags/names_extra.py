from django.template.defaultfilters import stringfilter
from django import template
import urllib, hashlib, sys

register = template.Library()

@register.filter
@stringfilter
def capsname(value):
    "Capitalizes full name"

    return ' '.join([ (name.capitalize() if 
                      (name not in ("de", "da", "e")) else name)
                      for name in value.lower().split() ])

@register.filter
@stringfilter
def gravatar_url(value, default="404", size=32):
    "Gets gravatar URL"
   
    # returns generated URL
    return "http://www.gravatar.com/avatar/%s?%s" % (
         hashlib.md5(value.lower()).hexdigest(),
         urllib.urlencode({'d':default, 's':str(size)})
        )

