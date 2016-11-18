from . import GCTestCase
from ..handlers import EventHandler


class EventsTestCase(GCTestCase):

    def test_event_actions_connected(self):
        for client_property, actions in EventHandler.ACTIONS.items():
            for method_name, signal in actions.items():
                self.assertEqual(1, len(signal.receivers))
