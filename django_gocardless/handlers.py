from gocardless_pro.resources import Event


class EventHandler(object):

    def __init__(self, event):
        if not isinstance(event, Event):
            raise ValueError('The EventHandler needs to be provided with an Event object.')

        self.event = event
