from django.conf import settings
from django import template

register = template.Library()

@register.simple_tag
def get_support_email():
    return getattr(settings, 'SUPPORT_EMAIL', 'support@nyumbafinder.co.ke')