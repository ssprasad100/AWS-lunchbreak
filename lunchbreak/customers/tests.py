from datetime import timedelta

import mock
from django.core.urlresolvers import reverse
from django.utils import timezone
from django_sms.models import Phone
from lunch.config import (BELGIUM, COST_GROUP_ADDITIONS, COST_GROUP_ALWAYS,
                          COST_GROUP_BOTH)
from lunch.exceptions import (BadRequest, DoesNotExist, LinkingError,
                              NoDeliveryToAddress)
from lunch.models import (Food, FoodType, HolidayPeriod, Ingredient,
                          IngredientGroup, IngredientRelation, Menu, Region,
                          Store)
from Lunchbreak.test import LunchbreakTestCase
from push_notifications.models import SERVICE_APNS, SERVICE_GCM
from rest_framework import status
from rest_framework.test import APIRequestFactory

from . import views
from .config import (DEMO_PHONE, INVITE_STATUS_ACCEPTED, INVITE_STATUS_IGNORED,
                     INVITE_STATUS_WAITING, ORDER_STATUS_COMPLETED,
                     RESERVATION_STATUS_USER, RESERVATION_STATUSES)
from .exceptions import (AlreadyMembership, InvalidStatusChange,
                         MaxSeatsExceeded, NoInvitePermissions,
                         OrderedFoodNotOriginal)
from .models import (Address, Group, Heart, Invite, Membership, Order,
                     OrderedFood, Reservation, User, UserToken)
from django.test.utils import override_settings


@override_settings(DEBUG=True)
class CustomersTests(LunchbreakTestCase):

    PHONE_USER = '+32472907604'
    NAME_USER = 'Meneer Aardappel'
    FORMAT = 'json'
    VALID_PHONE = '+32472907605'
    VALID_PHONE2 = '+32479427866'
    INVALID_PHONE = '+123456789'
    PIN = '123456'
    NAME = 'Meneer De Bolle'
    NAME_OTHER = 'Mevrouw De Bolle'
    EMAIL = 'meneer@debolle.com'
    EMAIL_OTHER = 'mevrouw@debolle.com'
    DEVICE = 'Test device'
    REGISTRATION_ID = '123456789'

    @mock.patch('googlemaps.Client.geocode')
    def setUp(self, mock_geocode):
        super(CustomersTests, self).setUp()
        self.factory = APIRequestFactory()

        self.phone = Phone.objects.create(
            phone=self.PHONE_USER,
            confirmed_at=timezone.now()
        )
        self.phone_other = Phone.objects.create(
            phone=self.VALID_PHONE2,
            confirmed_at=timezone.now()
        )

        self.mock_geocode_results(
            mock_geocode,
            lat=51.0111595,
            lng=3.9075993
        )

        self.user = User.objects.create(
            phone=self.phone,
            name=CustomersTests.NAME_USER
        )

        self.user_other = User.objects.create(
            phone=self.phone_other,
            name=CustomersTests.NAME_OTHER
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
            name='FoodType test',
            customisable=True
        )

        self.menu = Menu.objects.create(
            name='Menu test',
            store=self.store
        )

        self.ingredientgroup = IngredientGroup.objects.create(
            name='IngredientGroup test',
            foodtype=self.foodtype,
            store=self.store,
            cost=1
        )

        self.food = Food.objects.create(
            name='Food test',
            cost=100.00,
            foodtype=self.foodtype,
            menu=self.menu,
            store=self.store
        )

        ingredient_relations = [
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 1',
                    group=self.ingredientgroup,
                    store=self.store,
                    cost=0.1
                ),
                food=self.food,
                selected=True
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 2',
                    group=self.ingredientgroup,
                    store=self.store,
                    cost=0.1
                ),
                food=self.food,
                selected=True
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 3',
                    group=self.ingredientgroup,
                    store=self.store,
                    cost=0.1
                ),
                food=self.food,
                selected=True
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 4',
                    group=self.ingredientgroup,
                    store=self.store,
                    cost=0.1
                ),
                food=self.food,
                selected=True
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 5',
                    group=self.ingredientgroup,
                    store=self.store,
                    cost=0.1
                ),
                food=self.food,
                selected=False
            )
        ]
        for rel in ingredient_relations:
            rel.save()

        self.unique_food = Food.objects.create(
            name='Unique food',
            cost=1,
            foodtype=self.foodtype,
            menu=self.menu,
            store=self.store
        )

        self.unique_ingredient = Ingredient.objects.create(
            name='Unique ingredient',
            group=self.ingredientgroup,
            store=self.store,
            cost=0.1
        )

        self.unique_ingredientrelation = IngredientRelation.objects.create(
            ingredient=self.unique_ingredient,
            food=self.unique_food,
            selected=True
        )

        HolidayPeriod.objects.bulk_create([
            HolidayPeriod(
                store=self.store,
                start=timezone.now() - timedelta(days=10),
                end=timezone.now() + timedelta(days=10),
                closed=False
            )
        ])

    def test_registration(self):
        url = reverse('customers-user-register')
        content = {
            'phone': CustomersTests.VALID_PHONE
        }

        view = views.UserViewSet
        view_actions = {
            'post': 'register'
        }

        # As long as the name is not in the database, it should return 201
        for i in range(0, 2):
            request = self.factory.post(url, content)
            response = self.as_view(request, view, view_actions)
            response.render()
            self.assertEqual(len(response.content), 0)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @mock.patch('customers.models.User.register')
    def test_registration_demo(self, mock_register):
        url = reverse('customers-user-register')
        content = {
            'phone': DEMO_PHONE
        }

        view = views.UserViewSet
        view_actions = {
            'post': 'register'
        }

        # The demo should always return 200
        request = self.factory.post(url, content)
        response = self.as_view(request, view, view_actions)
        response.render()
        self.assertEqual(len(response.content), 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(mock_register.called)

    @mock.patch('customers.models.User.register')
    def test_registration_invalid(self, mock_register):
        url = reverse('customers-user-register')
        content = {
            'phone': CustomersTests.INVALID_PHONE
        }

        view = views.UserViewSet
        view_actions = {
            'post': 'register'
        }

        request = self.factory.post(url, content)
        response = self.as_view(request, view, view_actions)
        self.assertEqualException(response, BadRequest)
        self.assertFalse(mock_register.called)

        content = {}

        request = self.factory.post(url, content)
        response = self.as_view(request, view, view_actions)
        self.assertEqualException(response, BadRequest)
        self.assertFalse(mock_register.called)

    def test_login(self):
        url = reverse('customers-user-login')
        content = {
            'phone': CustomersTests.VALID_PHONE,
            'pin': CustomersTests.PIN,
            'token': {
                'device': CustomersTests.DEVICE,
                'service': SERVICE_APNS,
                'registration_id': CustomersTests.REGISTRATION_ID
            }
        }

        view = views.UserViewSet
        view_actions = {
            'post': 'login'
        }

        # You cannot login without registering first
        request = self.factory.post(url, content)
        response = self.as_view(request, view, view_actions)
        self.assertEqualException(response, DoesNotExist)

        phone = Phone.objects.create(
            phone=CustomersTests.VALID_PHONE
        )
        user = User.objects.create(
            phone=phone
        )

        # A username is required
        request = self.factory.post(url, content)
        response = self.as_view(request, view, view_actions)
        self.assertEqualException(response, BadRequest)
        self.assertFalse(user.name)

        content['name'] = CustomersTests.NAME
        request = self.factory.post(url, content)
        response = self.as_view(request, view, view_actions)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user.refresh_from_db()
        tokens = UserToken.objects.filter(user=user)
        self.assertEqual(len(tokens), 1)
        identifier = tokens[0].identifier
        self.assertEqual(user.name, CustomersTests.NAME)

        content['name'] = CustomersTests.NAME_OTHER
        request = self.factory.post(url, content)
        response = self.as_view(request, view, view_actions)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        tokens = UserToken.objects.filter(user=user)
        self.assertEqual(len(tokens), 1)
        self.assertNotEqual(identifier, tokens[0].identifier)
        self.assertEqual(user.name, CustomersTests.NAME_OTHER)

        user.delete()

    @mock.patch('customers.models.User.login')
    def test_login_demo(self, mock_login):
        url = reverse('customers-user-login')

        content = {
            'phone': DEMO_PHONE,
            'pin': CustomersTests.PIN,
            'token': {
                'device': CustomersTests.DEVICE,
                'service': SERVICE_APNS,
                'registration_id': CustomersTests.REGISTRATION_ID
            }
        }

        view = views.UserViewSet
        view_actions = {
            'post': 'login'
        }

        # Demo account is only allowed when it's in the database
        request = self.factory.post(url, content)
        response = self.as_view(request, view, view_actions)
        self.assertEqualException(response, BadRequest)

        demo_pin = '1337'
        demo_phone = Phone.objects.create(
            phone=DEMO_PHONE,
            pin=demo_pin
        )
        demo = User.objects.create(
            phone=demo_phone
        )

        # Invalid pin
        request = self.factory.post(url, content)
        response = self.as_view(request, view, view_actions)
        self.assertEqualException(response, BadRequest)

        content['pin'] = demo_pin
        request = self.factory.post(url, content)
        response = self.as_view(request, view, view_actions)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserToken.objects.filter(user=demo).count(), 1)

        self.assertFalse(mock_login.called)

        demo.delete()

    def test_hearting(self):
        reverse_kwargs = {
            'pk': self.store.id
        }
        view_actions_heart = {
            'patch': 'heart'
        }
        view_actions_unheart = {
            'patch': 'unheart'
        }
        heart_url = reverse('customers-store-heart', kwargs=reverse_kwargs)
        unheart_url = reverse('customers-store-unheart', kwargs=reverse_kwargs)

        request = self.factory.patch(heart_url, {})
        response = self.authenticate_request(
            request,
            views.StoreViewSet,
            view_actions=view_actions_heart,
            pk=self.store.id
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Heart.objects.filter(user=self.user).count(), 1)

        request = self.factory.patch(heart_url, {})
        response = self.authenticate_request(
            request,
            views.StoreViewSet,
            view_actions=view_actions_heart,
            pk=self.store.id
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Heart.objects.filter(user=self.user).count(), 1)

        request = self.factory.patch(unheart_url, {})
        response = self.authenticate_request(
            request,
            views.StoreViewSet,
            view_actions=view_actions_unheart,
            pk=self.store.id
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Heart.objects.filter(user=self.user).count(), 0)

        request = self.factory.patch(unheart_url, {})

        response = self.authenticate_request(
            request,
            views.StoreViewSet,
            view_actions=view_actions_unheart,
            pk=self.store.id
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def clone_model(self, model):
        oldPk = model.pk
        model.pk = None
        model.save()
        return (model, model.__class__.objects.get(pk=oldPk),)

    @mock.patch('googlemaps.Client.geocode')
    def test_order(self, mock_geocode):
        """
        Test an order's total and whether marked Food's are deleted on save.
        """

        self.mock_geocode_results(mock_geocode)
        self.food, original = self.clone_model(self.food)

        content = {
            'receipt': (timezone.now() + timedelta(days=1)).isoformat(),
            'store': self.store.id,
            'orderedfood': [
                {
                    'original': original.id,
                    'total': original.cost * original.amount,
                    'amount': original.amount
                },
                {
                    'original': original.id,
                    'total': original.cost * original.amount,
                    'amount': original.amount
                }
            ]
        }
        url = reverse('customers-order-list')

        view_actions = {
            'post': 'create'
        }

        def create_order():
            request = self.factory.post(url, content)
            response = self.authenticate_request(
                request,
                views.OrderViewSet,
                view_actions=view_actions
            )
            if response.status_code == status.HTTP_201_CREATED:
                order = Order.objects.get(id=response.data['id'])
                self.assertEqual(order.total, original.cost * 2)
                return (response, order)
            return (response, None)

        response, order = create_order()
        response.render()
        self.assertIsNotNone(order)

        original.delete()
        self.assertTrue(original.deleted)
        order.status = ORDER_STATUS_COMPLETED
        order.save()
        self.assertRaises(
            Food.DoesNotExist,
            Food.objects.get,
            id=original.id
        )
        self.assertEqual(
            OrderedFood.objects.filter(
                placed_order=order
            ).count(),
            0
        )

        # Test delivery address exceptions
        self.food, original = self.clone_model(self.food)
        content['orderedfood'] = [
            {
                'original': original.id,
                'total': original.cost * original.amount,
                'amount': original.amount
            },
            {
                'original': original.id,
                'total': original.cost * original.amount,
                'amount': original.amount
            }
        ]

        address = Address.objects.create(
            user=self.user,
            country='België',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )
        address, address_other = self.clone_model(address)
        address_other.user = self.user_other
        address_other.save()

        content['delivery_address'] = address.id
        response, order = create_order()
        self.assertEqualException(response, NoDeliveryToAddress)

        content['delivery_address'] = address_other.id
        response, order = create_order()
        self.assertEqualException(response, LinkingError)

        # Orders meant to be picked up cannot have receipt be None
        del content['receipt']
        del content['delivery_address']
        response, order = create_order()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_orderedfood_calculate_cost(self):
        self.ingredientgroup.calculation = COST_GROUP_ALWAYS
        self.ingredientgroup.save()

        selected_ingredientrelations = self.food.ingredientrelation_set.filter(
            selected=True
        )
        selected_ingredients = [r.ingredient for r in selected_ingredientrelations]
        selected_ingredient = selected_ingredients[0]
        deselected_ingredient = self.food.ingredientrelation_set.filter(
            selected=False
        ).first().ingredient

        # Check whether the calculated cost with all of the ingredients
        # remains the same.
        self.assertEqual(
            OrderedFood.calculate_cost(
                selected_ingredients,
                self.food
            ),
            self.food.cost
        )

        # Check whether the calculated cost with none of the ingredients
        # equals that of the food - the cost of the ingredient group
        self.assertEqual(
            OrderedFood.calculate_cost(
                [],
                self.food
            ),
            self.food.cost - self.ingredientgroup.cost
        )

        # Check whether the calculated cost with 1 missing ingredient
        # remains the same.
        selected_ingredients.remove(selected_ingredient)
        self.assertEqual(
            OrderedFood.calculate_cost(
                selected_ingredients,
                self.food
            ),
            self.food.cost
        )

        # Check whether the calculated cost with 1 added ingredient
        # remains the same.
        selected_ingredients.append(selected_ingredient)
        selected_ingredients.append(deselected_ingredient)
        self.assertEqual(
            OrderedFood.calculate_cost(
                selected_ingredients,
                self.food
            ),
            self.food.cost
        )
        selected_ingredients.remove(deselected_ingredient)

        # Check whether the value changes only when adding
        self.ingredientgroup.calculation = COST_GROUP_ADDITIONS
        self.ingredientgroup.save()
        deselected_ingredient.group.refresh_from_db()

        # Check whether the calculated cost with all of the ingredients
        # remains the same.
        self.assertEqual(
            OrderedFood.calculate_cost(
                selected_ingredients,
                self.food
            ),
            self.food.cost
        )

        # Check whether the calculated cost with 1 missing ingredient
        # remains the same.
        selected_ingredients.remove(selected_ingredient)
        self.assertEqual(
            OrderedFood.calculate_cost(
                selected_ingredients,
                self.food
            ),
            self.food.cost
        )

        # Check whether the calculated cost with 1 added ingredient
        # remains the same.
        selected_ingredients.append(selected_ingredient)
        selected_ingredients.append(deselected_ingredient)
        self.assertEqual(
            OrderedFood.calculate_cost(
                selected_ingredients,
                self.food
            ),
            self.food.cost + deselected_ingredient.cost
        )
        selected_ingredients.remove(deselected_ingredient)

        # Check whether the calculated cost with none of the ingredients
        # equals that of the food - the cost of the ingredient group
        self.assertEqual(
            OrderedFood.calculate_cost(
                [],
                self.food
            ),
            self.food.cost - self.ingredientgroup.cost
        )

        # Check whether the value changes only when adding and removing
        self.ingredientgroup.calculation = COST_GROUP_BOTH
        self.ingredientgroup.save()

        # Check whether the calculated cost with all of the ingredients
        # remains the same.
        self.assertEqual(
            OrderedFood.calculate_cost(
                selected_ingredients,
                self.food
            ),
            self.food.cost
        )

        # Check whether the calculated cost with 1 missing ingredient
        # remains the same.
        selected_ingredients.remove(selected_ingredient)
        self.assertEqual(
            OrderedFood.calculate_cost(
                selected_ingredients,
                self.food
            ),
            self.food.cost - selected_ingredient.cost
        )

        # Check whether the calculated cost with 1 added ingredient
        # remains the same.
        selected_ingredients.append(selected_ingredient)
        selected_ingredients.append(deselected_ingredient)
        self.assertEqual(
            OrderedFood.calculate_cost(
                selected_ingredients,
                self.food
            ),
            self.food.cost + deselected_ingredient.cost
        )
        selected_ingredients.remove(deselected_ingredient)

        # Check whether the calculated cost with none of the ingredients
        # equals that of the food - the separate costs of the ingredients
        cost_separate_ingredients = 0
        for ingredient in selected_ingredients:
            cost_separate_ingredients += ingredient.cost
        self.assertEqual(
            OrderedFood.calculate_cost(
                [],
                self.food
            ),
            self.food.cost - cost_separate_ingredients
        )

    def test_order_with_ingredients(self):
        selected_ingredientrelations = self.food.ingredientrelation_set.filter(
            selected=True
        )
        selected_ingredients = [r.ingredient for r in selected_ingredientrelations]

        orderedfood = [
            {
                'original': self.food,
                'amount': 1,
                'total': self.food.cost
            }
        ]

        order = Order.objects.create_with_orderedfood(
            orderedfood=orderedfood,
            user=self.user,
            store=self.store,
            receipt=timezone.now() + timedelta(hours=1)
        )

        of = order.orderedfood.all().first()
        self.assertTrue(of.is_original)
        self.assertFalse(of.ingredients.all().exists())

        # Adding the same ingredients as selected on the food doesn't set the
        # ingredients on the OrderedFood.
        orderedfood[0]['ingredients'] = selected_ingredients
        order = Order.objects.create_with_orderedfood(
            orderedfood=orderedfood,
            user=self.user,
            store=self.store,
            receipt=timezone.now() + timedelta(hours=1)
        )

        of = order.orderedfood.all().first()
        self.assertTrue(of.is_original)
        self.assertFalse(of.ingredients.all().exists())

        orderedfood[0]['ingredients'] = [self.unique_ingredient]
        self.assertEqual(
            Food.objects.closest(
                ingredients=orderedfood[0]['ingredients'],
                original=self.food
            ),
            self.unique_food
        )
        self.assertRaises(
            OrderedFoodNotOriginal,
            Order.objects.create_with_orderedfood,
            orderedfood=orderedfood,
            user=self.user,
            store=self.store,
            receipt=timezone.now() + timedelta(hours=1)
        )

    def test_token_update(self):
        """
        Test whether a user can change his token's registration_id.
        """

        self.food, original = self.clone_model(self.food)

        content = {}
        view_actions_patch = {
            'patch': 'token'
        }
        view_actions_put = {
            'put': 'token'
        }
        url = reverse('customers-user-token')

        request = self.factory.patch(url, content)
        response = self.authenticate_request(
            request, views.UserViewSet, view_actions=view_actions_patch)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        request = self.factory.put(url, content)
        response = self.authenticate_request(
            request, views.UserViewSet, view_actions=view_actions_put)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content['registration_id'] = 'blab'

        request = self.factory.patch(url, content)
        response = self.authenticate_request(
            request, views.UserViewSet, view_actions=view_actions_patch)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.usertoken.refresh_from_db()
        self.assertEqual(self.usertoken.registration_id, content['registration_id'])

        self.usertoken.registration_id = 'else'
        self.usertoken.save()

        request = self.factory.put(url, content)
        response = self.authenticate_request(
            request, views.UserViewSet, view_actions=view_actions_put)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.usertoken.refresh_from_db()
        self.assertEqual(self.usertoken.registration_id, content['registration_id'])

        self.usertoken.service = SERVICE_APNS
        self.usertoken.save()
        content['service'] = SERVICE_GCM

        request = self.factory.patch(url, content)
        response = self.authenticate_request(
            request, views.UserViewSet, view_actions=view_actions_patch)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.usertoken.refresh_from_db()
        self.assertEqual(self.usertoken.registration_id, content['registration_id'])
        self.assertEqual(self.usertoken.service, content['service'])

        self.usertoken.service = SERVICE_APNS
        self.usertoken.save()

        request = self.factory.put(url, content)
        response = self.authenticate_request(
            request, views.UserViewSet, view_actions=view_actions_put)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.usertoken.refresh_from_db()
        self.assertEqual(self.usertoken.registration_id, content['registration_id'])
        self.assertEqual(self.usertoken.service, content['service'])

    def test_reservation_create(self):
        """
        Test whether a user can create a reservation. But cannot set specific
        attributes he is not allowed to.
        """

        url = reverse('customers-user-reservation')

        content = {
            'store': self.store.id,
            # No need to check reservation_time, see Store.is_open test
            'reservation_time': (
                timezone.now() + timedelta(days=1)
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

    def test_reservation_update(self):
        reservation = Reservation.objects.create(
            user=self.user,
            store=self.store,
            # For some reason Travis running Python 2.7.9 saves microseconds and 2.7.10 doesn't
            reservation_time=(timezone.now() + timedelta(days=1)).replace(microsecond=0),
            seats=self.store.seats_max
        )

        kwargs = {'pk': reservation.id}
        url = reverse('customers-reservation', kwargs=kwargs)

        attributed_denied = {
            'seats': self.store.seats_max - 1,
            'reservation_time': (
                timezone.now() + timedelta(days=2)
            ).isoformat(),
            'store': self.store_other.id,
            'user': self.user_other.id
        }

        for attribute, value in attributed_denied.items():
            value_original = getattr(reservation, attribute)
            content = {
                attribute: value
            }

            request = self.factory.patch(url, content)
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

        for status_from, status_to in status_tree.items():
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

    @mock.patch('googlemaps.Client.geocode')
    def test_address_delete(self, mock_geocode):
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
