from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.inclusion_tag('timeline/icon.html')
def icon(id, href, cssid, title, iconname):
    return { "href": href + id,
             "id": cssid + id,
             "title": title,
             "iconname": iconname}

@register.inclusion_tag('timeline/mstext.html', takes_context = True)
def mstext(context):
    lang = context['request'].LANGUAGE_CODE
    ms = context['milestone']
    return { 'text' : ms.get_text(lang)}

