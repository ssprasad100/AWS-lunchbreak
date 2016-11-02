from datetime import timedelta

import pendulum
from django.core.urlresolvers import reverse
from rest_framework import status

from . import CustomersTestCase
from .. import views
from ..config import RESERVATION_STATUS_USER, RESERVATION_STATUSES
from ..exceptions import MaxSeatsExceeded
from ..models import Reservation


class ReservationTestCase(CustomersTestCase):

    def test_create(self):
        """
        Test whether a user can create a reservation. But cannot set specific
        attributes he is not allowed to.
        """

        url = reverse('customers-user-reservation')

        content = {
            'store': self.store.id,
            # No need to check reservation_time, see Store.is_open test
            'reservation_time': (
                pendulum.now(self.store.timezone) + timedelta(days=1)
            ).isoformat(),
            'seats': 0
        }

        request = self.factory.post(url, content)
        response = self.authenticate_request(request, views.ReservationMultiView)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content['seats'] = self.store.seats_max + 1

        request = self.factory.post(url, content)
        response = self.authenticate_request(request, views.ReservationMultiView)
        self.assertEqualException(response, MaxSeatsExceeded)

        content['seats'] = self.store.seats_max

        request = self.factory.post(url, content)
        response = self.authenticate_request(request, views.ReservationMultiView)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        Reservation.objects.all().delete()

    def test_update(self):
        reservation = Reservation.objects.create(
            user=self.user,
            store=self.store,
            reservation_time=(
                pendulum.now(self.store.timezone) + timedelta(days=1)
            ).replace(microsecond=0),
            seats=self.store.seats_max
        )
        print(reservation.reservation_time)
        reservation.save()
        print(reservation.reservation_time)

        kwargs = {'pk': reservation.id}
        url = reverse('customers-reservation', kwargs=kwargs)

        attributed_denied = {
            'seats': self.store.seats_max - 1,
            'reservation_time': (
                pendulum.now(self.store.timezone) + timedelta(days=2)
            ).isoformat(),
            'store': self.store_other.id,
            'user': self.user_other.id
        }

        for attribute, value in attributed_denied.items():
            original_value = getattr(reservation, attribute)
            content = {
                attribute: value
            }

            request = self.factory.patch(url, content)
            response = self.authenticate_request(request, views.ReservationSingleView, **kwargs)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            reservation.refresh_from_db()
            new_value = getattr(reservation, attribute)
            print('self.store.timezone', self.store.timezone)
            print('new_value', new_value)
            print('original_value', original_value)
            print('reservation.reservation_time', reservation.reservation_time)
            self.assertEqual(new_value, original_value)

        for tuple_allowed in RESERVATION_STATUS_USER:
            status_original = reservation.status
            status_allowed = tuple_allowed[0]

            content = {
                'status': status_allowed
            }

            request = self.factory.patch(url, content)
            response = self.authenticate_request(request, views.ReservationSingleView, **kwargs)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            reservation.refresh_from_db()
            self.assertEqual(reservation.status, status_allowed)

            reservation.status = status_original
            reservation.save()

        for tuple_denied in RESERVATION_STATUSES:
            if tuple_denied in RESERVATION_STATUS_USER:
                continue

            status_original = reservation.status
            status_denied = tuple_denied[0]

            content = {
                'status': status_denied
            }

            request = self.factory.patch(url, content)
            response = self.authenticate_request(request, views.ReservationSingleView, **kwargs)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            reservation.refresh_from_db()
            self.assertEqual(reservation.status, status_original)
