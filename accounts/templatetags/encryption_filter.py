from django import template

from accounts.utils import decrypt_data

register  = template.Library()

@register.filter
def decrypt_and_slice(value, slice_range):
    """Decrypt the value and then slice it"""
    if not value:
        return value
    
    decrypted = decrypt_data(value)
    if not decrypted:
        return "******"
    
    # Handle slice range like "8" or "4:8"
    if ':' in slice_range:
        start, end = slice_range.split(':')
        start = int(start) if start else 0
        end = int(end) if end else None
        return decrypted[start:end] + '******'
    else:
        slice_point = int(slice_range)
        return decrypted[:slice_point] + '******'

@register.filter
def mask_sensitive(value, arg="4:4"):
    """
        Mask sensitive data with configurable visible chars and asterisk count
        Usage: {{ value|mask_sensitive:"visible:asterisks" }}
        Default: {{ value|mask_sensitive }} = 4 visible + 4 asterisks
    """
    if not value:
        return value
    
    # Parse the argument
    try:
        if ':' in arg:
            visible_chars, asterisk_count = map(int, arg.split(':'))
        else:
            visible_chars = int(arg)
            asterisk_count = 4  # default asterisks
    except (ValueError, TypeError):
        visible_chars = 4
        asterisk_count = 4
    
    decrypted = decrypt_data(value)
    if not decrypted:
        return "*" * asterisk_count
    
    if len(decrypted) <= visible_chars:
        return decrypted
    
    return decrypted[:visible_chars] + '*' * asterisk_count