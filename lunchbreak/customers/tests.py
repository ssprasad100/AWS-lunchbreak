# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta

import mock
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils import timezone
from lunch.exceptions import BadRequest, DoesNotExist
from lunch.models import (Food, FoodCategory, FoodType, HolidayPeriod,
                          Ingredient, IngredientGroup, IngredientRelation,
                          Store)
from Lunchbreak.test import LunchbreakTestCase
from push_notifications.models import SERVICE_APNS, SERVICE_GCM
from rest_framework import status
from rest_framework.test import APIRequestFactory

from . import views
from .config import *  # NOQA
from .exceptions import (AlreadyMembership, InvalidStatusChange,
                         MaxSeatsExceeded, NoInvitePermissions)
from .models import (Group, Heart, Invite, Membership, Order, OrderedFood,
                     Reservation, User, UserToken)


class CustomersTests(LunchbreakTestCase):

    PHONE_USER = '+32472907604'
    NAME_USER = 'Meneer Aardappel'
    FORMAT = 'json'
    VALID_PHONE = '+32472907605'
    VALID_PHONE2 = '+32472907606'
    INVALID_PHONE = '+123456789'
    PIN = '123456'
    NAME = 'Meneer De Bolle'
    NAME_ALTERNATE = 'Mevrouw De Bolle'
    EMAIL = 'meneer@debolle.com'
    EMAIL_ALTERNATE = 'mevrouw@debolle.com'
    DEVICE = 'Test device'
    REGISTRATION_ID = '123456789'

    @mock.patch('requests.Response.json')
    @mock.patch('requests.get')
    def setUp(self, mock_get, mock_json):
        super(CustomersTests, self).setUp()
        self.factory = APIRequestFactory()

        self.mock_address_response(
            mock_get,
            mock_json,
            lat=51.0111595,
            lng=3.9075993
        )

        self.user = User.objects.create(
            phone=CustomersTests.PHONE_USER,
            name=CustomersTests.NAME_USER
        )

        self.user_other = User.objects.create(
            phone=CustomersTests.VALID_PHONE2,
            name=CustomersTests.NAME_ALTERNATE
        )

        self.usertoken = UserToken.objects.create(
            identifier='something',
            device='something',
            user=self.user,
            registration_id='something',
            service=SERVICE_APNS
        )

        self.store = Store.objects.create(
            name='CustomersTests',
            country='België',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )

        self.store_other = Store.objects.create(
            name='CustomersTestsOther',
            country='België',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )

        self.foodtype = FoodType.objects.create(
            name='FoodType test'
        )

        self.foodcategory = FoodCategory.objects.create(
            name='FoodCategory test',
            store=self.store
        )

        self.ingredientGroup = IngredientGroup.objects.create(
            name='IngredientGroup test',
            foodtype=self.foodtype,
            store=self.store
        )

        self.food = Food.objects.create(
            name='Food test',
            cost=1.00,
            foodtype=self.foodtype,
            category=self.foodcategory,
            store=self.store
        )

        IngredientRelation.objects.bulk_create([
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 1',
                    group=self.ingredientGroup,
                    store=self.store
                ),
                food=self.food
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 2',
                    group=self.ingredientGroup,
                    store=self.store
                ),
                food=self.food
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 3',
                    group=self.ingredientGroup,
                    store=self.store
                ),
                food=self.food
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 4',
                    group=self.ingredientGroup,
                    store=self.store
                ),
                food=self.food
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 5',
                    group=self.ingredientGroup,
                    store=self.store
                ),
                food=self.food
            )
        ])

        HolidayPeriod.objects.bulk_create([
            HolidayPeriod(
                store=self.store,
                start=timezone.now() - timedelta(days=10),
                end=timezone.now() + timedelta(days=10),
                closed=False
            )
        ])

    @mock.patch('customers.models.User.digits_register')
    @mock.patch('customers.models.User.digits_login')
    def test_registration(self, mock_login, mock_register):
        mock_info = {
            'digits_id': 123,
            'request_id': 123
        }
        mock_login.return_value = mock_info
        mock_register.return_value = mock_info

        url = reverse('user-registration')
        content = {
            'phone': CustomersTests.VALID_PHONE
        }

        # As long as the name is not in the database, it should return 201
        for i in range(0, 2):
            response = self.client.post(url, content, format=CustomersTests.FORMAT)
            self.assertEqual(response.content, '')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        User.objects.filter(phone=CustomersTests.VALID_PHONE).delete()

    @mock.patch('customers.models.User.register')
    def test_registration_demo(self, mock_register):
        url = reverse('user-registration')
        content = {
            'phone': DEMO_PHONE
        }

        # The demo should always return 200
        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqual(response.content, '')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(mock_register.called)

    @mock.patch('customers.models.User.register')
    def test_registration_invalid(self, mock_register):
        url = reverse('user-registration')
        content = {
            'phone': CustomersTests.INVALID_PHONE
        }

        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqualException(response, BadRequest)
        self.assertFalse(mock_register.called)

        content = {}

        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqualException(response, BadRequest)
        self.assertFalse(mock_register.called)

    @mock.patch('customers.digits.Digits.signing_confirm')
    @mock.patch('customers.digits.Digits.register_confirm')
    def test_login(self, mock_registration, mock_signin):
        mock_registration.return_value = {
            'id': 123
        }
        mock_signin.return_value = None

        url = reverse('user-login')
        content = {
            'phone': CustomersTests.VALID_PHONE,
            'pin': CustomersTests.PIN,
            'token': {
                'device': CustomersTests.DEVICE,
                'service': SERVICE_APNS,
                'registration_id': CustomersTests.REGISTRATION_ID
            }
        }

        # You cannot login without registering first
        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqualException(response, DoesNotExist)

        user = User.objects.create(
            phone=CustomersTests.VALID_PHONE
        )

        # A username is required
        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqualException(response, BadRequest)
        self.assertFalse(user.name)
        self.assertFalse(user.email)
        self.assertFalse(user.confirmed_at)

        # An email is required
        content['name'] = CustomersTests.NAME
        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqualException(response, BadRequest)
        self.assertFalse(user.name)
        self.assertFalse(user.email)
        self.assertFalse(user.confirmed_at)

        content['email'] = CustomersTests.EMAIL
        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user.refresh_from_db()
        tokens = UserToken.objects.filter(user=user)
        self.assertEqual(len(tokens), 1)
        identifier = tokens[0].identifier
        self.assertTrue(user.confirmed_at)
        self.assertEqual(user.name, CustomersTests.NAME)
        self.assertEqual(user.email, CustomersTests.EMAIL)
        confirmed_at = user.confirmed_at

        content['name'] = CustomersTests.NAME_ALTERNATE
        content['email'] = CustomersTests.EMAIL_ALTERNATE
        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        tokens = UserToken.objects.filter(user=user)
        self.assertEqual(len(tokens), 1)
        self.assertNotEqual(identifier, tokens[0].identifier)
        self.assertEqual(user.name, CustomersTests.NAME_ALTERNATE)
        self.assertEqual(user.email, CustomersTests.EMAIL_ALTERNATE)
        self.assertEqual(user.confirmed_at, confirmed_at)

        user.delete()

    @mock.patch('customers.models.User.login')
    def test_login_demo(self, mock_login):
        url = reverse('user-login')

        content = {
            'phone': DEMO_PHONE,
            'pin': CustomersTests.PIN,
            'token': {
                'device': CustomersTests.DEVICE,
                'service': SERVICE_APNS,
                'registration_id': CustomersTests.REGISTRATION_ID
            }
        }

        # Demo account is only allowed when it's in the database
        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqualException(response, BadRequest)

        demoPin = '1337'
        demo = User.objects.create(phone=DEMO_PHONE, request_id=demoPin, digits_id=DEMO_DIGITS_ID)

        # Invalid pin
        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqualException(response, BadRequest)

        content['pin'] = demoPin
        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserToken.objects.filter(user=demo).count(), 1)

        self.assertFalse(mock_login.called)

        demo.delete()

    def test_hearting(self):
        heart_kwargs = {'option': 'heart', 'pk': self.store.id}
        heart_url = reverse('store-heart', kwargs=heart_kwargs)
        unheart_kwargs = {'option': 'unheart', 'pk': self.store.id}
        unheart_url = reverse('store-heart', kwargs=unheart_kwargs)

        request = self.factory.patch(heart_url, {}, format=CustomersTests.FORMAT)
        response = self.authenticate_request(request, views.StoreHeartView, **heart_kwargs)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Heart.objects.filter(user=self.user).count(), 1)

        request = self.factory.patch(heart_url, {}, format=CustomersTests.FORMAT)
        response = self.authenticate_request(request, views.StoreHeartView, **heart_kwargs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Heart.objects.filter(user=self.user).count(), 1)

        request = self.factory.patch(unheart_url, {}, format=CustomersTests.FORMAT)
        response = self.authenticate_request(request, views.StoreHeartView, **unheart_kwargs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Heart.objects.filter(user=self.user).count(), 0)

        request = self.factory.patch(unheart_url, {}, format=CustomersTests.FORMAT)
        self.assertRaises(
            Http404, self.authenticate_request, request, views.StoreHeartView, **unheart_kwargs)

    def clone_model(self, model):
        oldPk = model.pk
        model.pk = None
        model.save()
        return (model, model.__class__.objects.get(pk=oldPk),)

    def test_order(self):
        '''
        Test whether an order's total, paid and marked Food's are deleted on save.
        '''

        self.food, original = self.clone_model(self.food)

        content = {
            'pickup': (timezone.now() + timedelta(days=1)).strftime(settings.DATETIME_FORMAT),
            'store': self.store.id,
            'orderedfood': [
                {
                    'original': original.id,
                    'cost': original.cost,
                    'amount': original.amount
                },
                {
                    'original': original.id,
                    'cost': original.cost,
                    'amount': original.amount
                }
            ]
        }
        url = reverse('order')

        request = self.factory.post(url, content, format=CustomersTests.FORMAT)
        response = self.authenticate_request(request, views.OrderView)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.total, original.cost * 2)
        self.assertFalse(order.paid)

        order.status = ORDER_STATUS_COMPLETED
        order.save()
        self.assertTrue(order.paid)

        request = self.factory.post(url, content, format=CustomersTests.FORMAT)
        response = self.authenticate_request(request, views.OrderView)
        order = Order.objects.get(id=response.data['id'])

        original.delete()
        self.assertTrue(original.deleted)
        order.status = ORDER_STATUS_COMPLETED
        order.save()
        self.assertRaises(Food.DoesNotExist, Food.objects.get, id=original.id)
        self.assertEqual(OrderedFood.objects.filter(order=order).count(), 0)

    def test_token_update(self):
        '''
        Test whether a user can change his token's registration_id.
        '''

        self.food, original = self.clone_model(self.food)

        content = {}
        url = reverse('user-token')

        request = self.factory.patch(url, content, format=CustomersTests.FORMAT)
        response = self.authenticate_request(request, views.UserTokenUpdateView)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        request = self.factory.put(url, content, format=CustomersTests.FORMAT)
        response = self.authenticate_request(request, views.UserTokenUpdateView)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content['registration_id'] = 'blab'

        request = self.factory.patch(url, content, format=CustomersTests.FORMAT)
        response = self.authenticate_request(request, views.UserTokenUpdateView)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.usertoken.refresh_from_db()
        self.assertEqual(self.usertoken.registration_id, content['registration_id'])

        self.usertoken.registration_id = 'else'
        self.usertoken.save()

        request = self.factory.put(url, content, format=CustomersTests.FORMAT)
        response = self.authenticate_request(request, views.UserTokenUpdateView)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.usertoken.refresh_from_db()
        self.assertEqual(self.usertoken.registration_id, content['registration_id'])

        self.usertoken.service = SERVICE_APNS
        self.usertoken.save()
        content['service'] = SERVICE_GCM

        request = self.factory.patch(url, content, format=CustomersTests.FORMAT)
        response = self.authenticate_request(request, views.UserTokenUpdateView)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.usertoken.refresh_from_db()
        self.assertEqual(self.usertoken.registration_id, content['registration_id'])
        self.assertEqual(self.usertoken.service, content['service'])

        self.usertoken.service = SERVICE_APNS
        self.usertoken.save()

        request = self.factory.put(url, content, format=CustomersTests.FORMAT)
        response = self.authenticate_request(request, views.UserTokenUpdateView)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.usertoken.refresh_from_db()
        self.assertEqual(self.usertoken.registration_id, content['registration_id'])
        self.assertEqual(self.usertoken.service, content['service'])

    def test_reservation_create(self):
        '''
        Test whether a user can create a reservation. But cannot set specific
        attributes he is not allowed to.
        '''

        url = reverse('user-reservation')

        content = {
            'store': self.store.id,
            # No need to check reservation_time, see Store.is_open test
            'reservation_time': (
                timezone.now() + timedelta(days=1)
            ).strftime(settings.DATETIME_FORMAT),
            'seats': 0
        }

        request = self.factory.post(url, content, format=CustomersTests.FORMAT)
        response = self.authenticate_request(request, views.ReservationMultiView)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content['seats'] = self.store.seats_max + 1

        request = self.factory.post(url, content, format=CustomersTests.FORMAT)
        response = self.authenticate_request(request, views.ReservationMultiView)
        self.assertEqualException(response, MaxSeatsExceeded)

        content['seats'] = self.store.seats_max

        request = self.factory.post(url, content, format=CustomersTests.FORMAT)
        response = self.authenticate_request(request, views.ReservationMultiView)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        Reservation.objects.all().delete()

    def test_reservation_update(self):
        reservation = Reservation.objects.create(
            user=self.user,
            store=self.store,
            # For some reason Travis running Python 2.7.9 saves microseconds and 2.7.10 doesn't
            reservation_time=(timezone.now() + timedelta(days=1)).replace(microsecond=0),
            seats=self.store.seats_max
        )

        kwargs = {'pk': reservation.id}
        url = reverse('reservation', kwargs=kwargs)

        attributed_denied = {
            'seats': self.store.seats_max - 1,
            'reservation_time': (
                timezone.now() + timedelta(days=2)
            ).strftime(settings.DATETIME_FORMAT),
            'store': self.store_other.id,
            'user': self.user_other.id
        }

        for attribute, value in attributed_denied.iteritems():
            value_original = getattr(reservation, attribute)
            content = {
                attribute: value
            }

            request = self.factory.patch(url, content, format=CustomersTests.FORMAT)
            response = self.authenticate_request(request, views.ReservationSingleView, **kwargs)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            reservation.refresh_from_db()
            self.assertEqual(getattr(reservation, attribute), value_original)

        for tuple_allowed in RESERVATION_STATUS_USER:
            status_original = reservation.status
            status_allowed = tuple_allowed[0]

            content = {
                'status': status_allowed
            }

            request = self.factory.patch(url, content, format=CustomersTests.FORMAT)
            response = self.authenticate_request(request, views.ReservationSingleView, **kwargs)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            reservation.refresh_from_db()
            self.assertEqual(reservation.status, status_allowed)

            reservation.status = status_original
            reservation.save()

        for tuple_denied in RESERVATION_STATUS:
            if tuple_denied in RESERVATION_STATUS_USER:
                continue

            status_original = reservation.status
            status_denied = tuple_denied[0]

            content = {
                'status': status_denied
            }

            request = self.factory.patch(url, content, format=CustomersTests.FORMAT)
            response = self.authenticate_request(request, views.ReservationSingleView, **kwargs)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            reservation.refresh_from_db()
            self.assertEqual(reservation.status, status_original)

    # def test_invite_already_invite(self):
    #     group = Group.create(
    #         name='Test',
    #         user=self.user
    #     )

    #     Invite.objects.create(
    #         group=group,
    #         user=self.user_other,
    #         invited_by=self.user
    #     )

    #     self.assertRaises(
    #         IntegrityError,
    #         Invite.objects.create,
    #         group=group,
    #         user=self.user_other,
    #         invited_by=self.user
    #     )

    #     Group.objects.all().delete()

    def test_invite_already_membership(self):
        group = Group.create(
            name='Test',
            user=self.user
        )

        Membership.objects.create(
            group=group,
            user=self.user_other
        )

        self.assertRaises(
            AlreadyMembership,
            Invite.objects.create,
            group=group,
            user=self.user_other,
            invited_by=self.user
        )

        Group.objects.all().delete()

    def test_invite_permission(self):
        group = Group.create(
            name='Test',
            user=self.user
        )

        Invite.objects.create(
            group=group,
            user=self.user_other,
            invited_by=self.user
        )

        self.assertRaises(
            NoInvitePermissions,
            Invite.objects.create,
            group=group,
            user=self.user,
            invited_by=self.user_other
        )

        Group.objects.all().delete()

    def test_invite_accept(self):
        group = Group.create(
            name='Test',
            user=self.user
        )

        invite = Invite.objects.create(
            group=group,
            user=self.user_other,
            invited_by=self.user
        )

        invite.status = INVITE_STATUS_ACCEPTED
        invite.save()

        self.assertIsNotNone(invite.membership)

    def test_invite_delete(self):
        group = Group.create(
            name='Test',
            user=self.user
        )

        invite = Invite.objects.create(
            group=group,
            user=self.user_other,
            invited_by=self.user
        )

        invite.delete()
        self.assertRaises(
            Invite.DoesNotExist,
            Invite.objects.get,
            group=group,
            user=self.user_other,
            invited_by=self.user,
        )

        invite.status = INVITE_STATUS_ACCEPTED
        invite.save()
        invite.delete()
        self.assertEqual(
            Invite.objects.filter(
                group=group,
                user=self.user_other,
                invited_by=self.user
            ).count(),
            1
        )

    def test_invite_status(self):
        group = Group.create(
            name='Test',
            user=self.user
        )

        status_tree = {
            INVITE_STATUS_WAITING: {
                'valid': [
                    INVITE_STATUS_ACCEPTED,
                    INVITE_STATUS_IGNORED
                ],
                'invalid': [
                ]
            },
            INVITE_STATUS_ACCEPTED: {
                'valid': [],
                'invalid': [
                    INVITE_STATUS_WAITING,
                    INVITE_STATUS_IGNORED
                ]
            },
            INVITE_STATUS_IGNORED: {
                'valid': [],
                'invalid': [
                    INVITE_STATUS_WAITING,
                    INVITE_STATUS_ACCEPTED
                ]
            },
        }

        def invite_reset(status):
            Invite.objects.all().delete()
            Membership.objects.filter(
                group=group,
                user=self.user_other
            ).delete()
            return Invite.objects.create(
                group=group,
                user=self.user_other,
                invited_by=self.user,
                status=status
            )

        for status_from, status_to in status_tree.iteritems():
            for status_valid in status_to['valid']:
                invite = invite_reset(status_from)
                invite.status = status_valid
                invite.save()
            for status_invalid in status_to['invalid']:
                invite = invite_reset(status_from)
                invite.status = status_invalid
                self.assertRaises(
                    InvalidStatusChange,
                    invite.save
                )

        Group.objects.all().delete()
