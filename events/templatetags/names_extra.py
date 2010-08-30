from django.template.defaultfilters import stringfilter
from django import template
from string import lower, capitalize

register = template.Library()

@register.filter
@stringfilter
def capsname(value):
	"Capitalizes full name"
	return ' '.join([ (capitalize(name) if 
					  (name not in ("de", "da", "e")) else name)
					  for name in lower(value).split() ])

