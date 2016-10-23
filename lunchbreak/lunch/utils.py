from datetime import datetime

from pendulum import Pendulum


def timezone_for_store(value, store):
    """Change the timezone of a datetime or pendulum object to that of the store."""
    if isinstance(value, datetime):
        value = Pendulum.instance(value)

    return value.timezone_(store.timezone)._datetime