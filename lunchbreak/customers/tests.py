# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta

import mock
from customers import views
from customers.config import (DEMO_DIGITS_ID, DEMO_PHONE,
                              ORDER_STATUS_COMPLETED, RESERVATION_STATUS,
                              RESERVATION_STATUS_USER)
from customers.exceptions import MaxSeatsExceeded, UserNameEmpty
from customers.models import (Heart, Order, OrderedFood, Reservation, User,
                              UserToken)
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
    DEVICE = 'Test device'
    REGISTRATION_ID = '123456789'

    def setUp(self):
        super(CustomersTests, self).setUp()
        self.factory = APIRequestFactory()

        self.user = User.objects.create(
            phone=CustomersTests.PHONE_USER,
            name=CustomersTests.NAME_USER
        )

        self.otherUser = User.objects.create(
            phone=CustomersTests.VALID_PHONE2,
            name=CustomersTests.NAME_ALTERNATE
        )

        self.userToken = UserToken.objects.create(
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

        self.otherStore = Store.objects.create(
            name='CustomersTestsOther',
            country='België',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )

        self.foodType = FoodType.objects.create(
            name='FoodType test'
        )

        self.foodCategory = FoodCategory.objects.create(
            name='FoodCategory test',
            store=self.store
        )

        self.ingredientGroup = IngredientGroup.objects.create(
            name='IngredientGroup test',
            foodType=self.foodType,
            store=self.store
        )

        self.food = Food.objects.create(
            name='Food test',
            cost=1.00,
            foodType=self.foodType,
            category=self.foodCategory,
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
    def testRegistration(self, mock_login, mock_register):
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
    def testDemoRegistration(self, mock_register):
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
    def testInvalidRegistration(self, mock_register):
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
    def testLogin(self, mock_registration, mock_signin):
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
        self.assertEqualException(response, UserNameEmpty)
        self.assertFalse(user.name)
        self.assertFalse(user.confirmed_at)

        content['name'] = CustomersTests.NAME
        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user.refresh_from_db()
        tokens = UserToken.objects.filter(user=user)
        self.assertEqual(len(tokens), 1)
        identifier = tokens[0].identifier
        self.assertTrue(user.confirmed_at)
        self.assertEqual(user.name, CustomersTests.NAME)
        confirmed_at = user.confirmed_at

        content['name'] = CustomersTests.NAME_ALTERNATE
        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        tokens = UserToken.objects.filter(user=user)
        self.assertEqual(len(tokens), 1)
        self.assertNotEqual(identifier, tokens[0].identifier)
        self.assertEqual(user.name, CustomersTests.NAME_ALTERNATE)
        self.assertEqual(user.confirmed_at, confirmed_at)

        user.delete()

    @mock.patch('customers.models.User.login')
    def testDemoLogin(self, mock_login):
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

    def testHearting(self):
        heartKwargs = {'option': 'heart', 'pk': self.store.id}
        heartUrl = reverse('store-heart', kwargs=heartKwargs)
        unheartKwargs = {'option': 'unheart', 'pk': self.store.id}
        unheartUrl = reverse('store-heart', kwargs=unheartKwargs)

        request = self.factory.patch(heartUrl, {}, format=CustomersTests.FORMAT)
        response = self.authenticateRequest(request, views.StoreHeartView, **heartKwargs)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Heart.objects.filter(user=self.user).count(), 1)

        request = self.factory.patch(heartUrl, {}, format=CustomersTests.FORMAT)
        response = self.authenticateRequest(request, views.StoreHeartView, **heartKwargs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Heart.objects.filter(user=self.user).count(), 1)

        request = self.factory.patch(unheartUrl, {}, format=CustomersTests.FORMAT)
        response = self.authenticateRequest(request, views.StoreHeartView, **unheartKwargs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Heart.objects.filter(user=self.user).count(), 0)

        request = self.factory.patch(unheartUrl, {}, format=CustomersTests.FORMAT)
        self.assertRaises(
            Http404, self.authenticateRequest, request, views.StoreHeartView, **unheartKwargs)

    def duplicateModel(self, model):
        oldPk = model.pk
        model.pk = None
        model.save()
        return (model, model.__class__.objects.get(pk=oldPk),)

    def testOrder(self):
        '''
        Test whether an order's total, paid and marked Food's are deleted on save.
        '''

        self.food, original = self.duplicateModel(self.food)

        content = {
            'pickup': (timezone.now() + timedelta(days=1)).strftime(settings.DATETIME_FORMAT),
            'store': self.store.id,
            'orderedFood': [
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
        response = self.authenticateRequest(request, views.OrderView)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.total, original.cost * 2)
        self.assertFalse(order.paid)

        order.status = ORDER_STATUS_COMPLETED
        order.save()
        self.assertTrue(order.paid)

        request = self.factory.post(url, content, format=CustomersTests.FORMAT)
        response = self.authenticateRequest(request, views.OrderView)
        order = Order.objects.get(id=response.data['id'])

        original.delete()
        self.assertTrue(original.deleted)
        order.status = ORDER_STATUS_COMPLETED
        order.save()
        self.assertRaises(Food.DoesNotExist, Food.objects.get, id=original.id)
        self.assertEqual(OrderedFood.objects.filter(order=order).count(), 0)

    def testTokenUpdate(self):
        '''
        Test whether a user can change his token's registration_id.
        '''

        self.food, original = self.duplicateModel(self.food)

        content = {}
        url = reverse('user-token')

        request = self.factory.patch(url, content, format=CustomersTests.FORMAT)
        response = self.authenticateRequest(request, views.UserTokenUpdateView)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        request = self.factory.put(url, content, format=CustomersTests.FORMAT)
        response = self.authenticateRequest(request, views.UserTokenUpdateView)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content['registration_id'] = 'blab'

        request = self.factory.patch(url, content, format=CustomersTests.FORMAT)
        response = self.authenticateRequest(request, views.UserTokenUpdateView)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.userToken.refresh_from_db()
        self.assertEqual(self.userToken.registration_id, content['registration_id'])

        self.userToken.registration_id = 'else'
        self.userToken.save()

        request = self.factory.put(url, content, format=CustomersTests.FORMAT)
        response = self.authenticateRequest(request, views.UserTokenUpdateView)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.userToken.refresh_from_db()
        self.assertEqual(self.userToken.registration_id, content['registration_id'])

        self.userToken.service = SERVICE_APNS
        self.userToken.save()
        content['service'] = SERVICE_GCM

        request = self.factory.patch(url, content, format=CustomersTests.FORMAT)
        response = self.authenticateRequest(request, views.UserTokenUpdateView)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.userToken.refresh_from_db()
        self.assertEqual(self.userToken.registration_id, content['registration_id'])
        self.assertEqual(self.userToken.service, content['service'])

        self.userToken.service = SERVICE_APNS
        self.userToken.save()

        request = self.factory.put(url, content, format=CustomersTests.FORMAT)
        response = self.authenticateRequest(request, views.UserTokenUpdateView)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.userToken.refresh_from_db()
        self.assertEqual(self.userToken.registration_id, content['registration_id'])
        self.assertEqual(self.userToken.service, content['service'])

    def testReservationCreate(self):
        '''
        Test whether a user can create a reservation. But cannot set specific attributes he is not allowed to.
        '''

        url = reverse('user-reservation')

        content = {
            'store': self.store.id,
            # No need to check reservation_time, see Store.checkOpen test
            'reservation_time': (timezone.now() + timedelta(days=1)).strftime(settings.DATETIME_FORMAT),
            'seats': 0
        }

        request = self.factory.post(url, content, format=CustomersTests.FORMAT)
        response = self.authenticateRequest(request, views.ReservationMultiView)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content['seats'] = self.store.maxSeats + 1

        request = self.factory.post(url, content, format=CustomersTests.FORMAT)
        response = self.authenticateRequest(request, views.ReservationMultiView)
        self.assertEqualException(response, MaxSeatsExceeded)

        content['seats'] = self.store.maxSeats

        request = self.factory.post(url, content, format=CustomersTests.FORMAT)
        response = self.authenticateRequest(request, views.ReservationMultiView)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        Reservation.objects.all().delete()

    def testReservationUpdate(self):
        reservation = Reservation.objects.create(
            user=self.user,
            store=self.store,
            # For some reason Travis running Python 2.7.9 saves microseconds and 2.7.10 doesn't
            reservation_time=(timezone.now() + timedelta(days=1)).replace(microsecond=0),
            seats=self.store.maxSeats
        )

        kwargs = {'pk': reservation.id}
        url = reverse('reservation', kwargs=kwargs)

        deniedAttributes = {
            'seats': self.store.maxSeats - 1,
            'reservation_time': (timezone.now() + timedelta(days=2)).strftime(settings.DATETIME_FORMAT),
            'store': self.otherStore.id,
            'user': self.otherUser.id
        }

        for attribute, value in deniedAttributes.iteritems():
            originalValue = getattr(reservation, attribute)
            content = {
                attribute: value
            }

            request = self.factory.patch(url, content, format=CustomersTests.FORMAT)
            response = self.authenticateRequest(request, views.ReservationSingleView, **kwargs)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            reservation.refresh_from_db()
            self.assertEqual(getattr(reservation, attribute), originalValue)

        for allowedTuple in RESERVATION_STATUS_USER:
            originalStatus = reservation.status
            allowedStatus = allowedTuple[0]

            content = {
                'status': allowedStatus
            }

            request = self.factory.patch(url, content, format=CustomersTests.FORMAT)
            response = self.authenticateRequest(request, views.ReservationSingleView, **kwargs)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            reservation.refresh_from_db()
            self.assertEqual(reservation.status, allowedStatus)

            reservation.status = originalStatus
            reservation.save()

        for deniedTuple in RESERVATION_STATUS:
            if deniedTuple in RESERVATION_STATUS_USER:
                continue

            originalStatus = reservation.status
            deniedStatus = deniedTuple[0]

            content = {
                'status': deniedStatus
            }

            request = self.factory.patch(url, content, format=CustomersTests.FORMAT)
            response = self.authenticateRequest(request, views.ReservationSingleView, **kwargs)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            reservation.refresh_from_db()
            self.assertEqual(reservation.status, originalStatus)
