from django import template
import datetime

register = template.Library()


@register.filter
def duration_format(value):
    """Форматирует timedelta в более привычный вид (например, '1 ч 30 мин')."""
    if isinstance(value, datetime.timedelta):
        total_seconds = int(value.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        if hours > 0 and minutes > 0:
            return f'{hours} ч {minutes} мин'
        elif hours > 0:
            return f'{hours} ч'
        else:
            return f'{minutes} мин'
    return value

register = template.Library()

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})
