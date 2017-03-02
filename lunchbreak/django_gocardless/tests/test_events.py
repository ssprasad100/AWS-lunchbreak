import mock
from gocardless_pro.resources.event import Event

from . import GCTestCase
from ..handlers import EventHandler
from ..models import Merchant
from ..utils import model_from_links


class EventsTestCase(GCTestCase):

    def test_event_actions_connected(self):
        for client_property, actions in EventHandler.ACTIONS.items():
            for method_name, signal in actions.items():
                self.assertEqual(1, len(signal.receivers))

    @mock.patch('django_gocardless.mixins.GCCacheMixin.client_from_settings')
    @mock.patch('django_gocardless.models.Payout.fetch')
    @mock.patch('gocardless_pro.resources.event.Event.Links.organisation', new_callable=mock.PropertyMock)
    def test_links_organisation(self, mock_organisation, mock_fetch, mock_client):
        organisation = 'organisation'
        access_token = 'access_token'

        Merchant.objects.create(
            organisation_id=organisation,
            access_token=access_token
        )
        mock_organisation.return_value = organisation
        links = Event.Links({
            'payout': 'something'
        })
        model_from_links(links, 'payout')

        self.assertTrue(mock_fetch.called)
        self.assertTrue(mock_client.called)
