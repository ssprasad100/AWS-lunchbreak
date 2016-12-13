from django.utils.translation import ugettext as _
from pendulum import Pendulum


def timezone_for_store(value, store):
    """Change the timezone of a datetime or pendulum object to that of the store."""
    if not isinstance(value, Pendulum):
        value = Pendulum.instance(value)

    return value.timezone_(store.timezone)._datetime


def uggettext_summation(items, fun):
    """Return a summation of items that works in the translated languages.

    Args:
        items: Iterable of items.
        fun: Callable with the first parameter being the item which returns a
        representation of the item.

    Returns:
        string
    """
    result = ''
    for index, item in enumerate(items):
        representation = fun(item)
        if index == 0:
            result += representation
        else:
            has_next = index < len(items) - 1
            if has_next:
                result += _(', %(item)s') % {
                    'item': representation
                }
            else:
                result += _(' en %(item)s') % {
                    'item': representation
                }
    return result
