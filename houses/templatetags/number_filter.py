from django import template

register = template.Library()

@register.filter
def humanize_number(value):
    """
        Converts a large number into a human-readable format. (e.g., 1500 -> 1.5K, 2000000 -> 2M)
    """
    try:
        num = int(value)
    except (ValueError, TypeError):
        return value
    
    if num < 1000:
        return str(num)
    elif num < 10000:
        # 1,000 - 9,999
        return f"{num/1000:.1f}K".replace('.0', '')
    elif num < 1000000:
        # 10,000 - 999,999
        return f"{num//1000}K"
    elif value < 10000000:
        # 1,000,000 - 9,999,999
        return f"{num/1000000:.1f}M".replace('.0', '')
    else:
        # 10,000,000 and above
        return f"{num//1000000}M"