from datetime import timedelta

import mock
from django.utils import timezone
from lunch.config import BELGIUM
from lunch.models import Region

from . import CustomersTestCase
from ..models import Address, Order


class AddressTestCase(CustomersTestCase):

    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('googlemaps.Client.geocode')
    def test_address_delete(self, mock_geocode, mock_timezone):
        # Disable address tests till delivery is enabled
        return

        self.mock_timezone_result(mock_timezone)
        self.mock_geocode_results(
            mock_geocode,
            lat=51.0111595,
            lng=3.9075993
        )

        address = Address.objects.create(
            user=self.user,
            country='België',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )

        address, address_clone = self.clone_model(address)
        address, address_clone2 = self.clone_model(address)

        # Deleting addresses without orders should go smoothly
        address_clone2.delete()
        self.assertIsNone(address_clone2.pk)

        region = Region.objects.create(
            country=BELGIUM,
            postcode='9230'
        )
        self.store.regions.add(region)
        order = Order.objects.create(
            user=self.user,
            store=self.store,
            receipt=timezone.now() + timedelta(hours=1),
            delivery_address=address
        )
        order, order_clone = self.clone_model(order)
        order_clone.delivery_address = address_clone
        order_clone.save()

        # Deleting addresses with an active order should stage it for deletion
        address.delete()
        self.assertIsNotNone(address.pk)
        self.assertTrue(address.deleted)

        # It should be deleted together with the order then
        order.delete()
        self.assertRaises(
            Order.DoesNotExist,
            order.refresh_from_db
        )
        self.assertRaises(
            Address.DoesNotExist,
            address.refresh_from_db
        )

        # Or when the status changes of the order
        address_clone.delete()
        self.assertIsNotNone(address_clone.pk)
        self.assertTrue(address_clone.deleted)

        order_clone.delete()
        self.assertRaises(
            Order.DoesNotExist,
            order_clone.refresh_from_db
        )
        self.assertRaises(
            Address.DoesNotExist,
            address_clone.refresh_from_db
        )
