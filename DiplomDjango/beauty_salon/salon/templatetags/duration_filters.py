from django import template

register = template.Library()

@register.filter
def duration_format(duration):
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    if hours > 0:
        return f"{hours} ч {minutes} мин" if minutes > 0 else f"{hours} ч"
    else:
        return f"{minutes} мин"
