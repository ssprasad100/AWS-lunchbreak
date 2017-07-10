import mock
from django.core.urlresolvers import reverse
from django_sms.models import Phone
from push_notifications.models import BareDevice
from rest_framework import status

from . import CustomersTestCase
from .. import views
from ..config import DEMO_PHONE
from ..models import Heart, User, UserToken


class UserTestCase(CustomersTestCase):

    def test_registration(self):
        url = reverse('customers:user-register')
        content = {
            'phone': self.VALID_PHONE
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
        url = reverse('customers:user-register')
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
        url = reverse('customers:user-register')
        content = {
            'phone': self.INVALID_PHONE
        }

        view = views.UserViewSet
        view_actions = {
            'post': 'register'
        }

        request = self.factory.post(url, content)
        response = self.as_view(request, view, view_actions)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(mock_register.called)

        content = {}

        request = self.factory.post(url, content)
        response = self.as_view(request, view, view_actions)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(mock_register.called)

    def test_login(self):
        url = reverse('customers:user-login')
        content = {
            'phone': self.VALID_PHONE,
            'pin': self.PIN,
            'token': {
                'device': self.DEVICE,
                'service': BareDevice.APNS,
                'registration_id': self.REGISTRATION_ID
            }
        }

        view = views.UserViewSet
        view_actions = {
            'post': 'login'
        }

        # You cannot login without registering first
        request = self.factory.post(url, content)
        response = self.as_view(request, view, view_actions)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        phone = Phone.objects.create(
            phone=self.VALID_PHONE
        )
        user = User.objects.create(
            phone=phone
        )

        # A username is required
        request = self.factory.post(url, content)
        response = self.as_view(request, view, view_actions)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user.name)

        content['name'] = self.NAME
        request = self.factory.post(url, content)
        response = self.as_view(request, view, view_actions)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user.refresh_from_db()
        tokens = UserToken.objects.filter(user=user)
        self.assertEqual(len(tokens), 1)
        identifier = tokens[0].identifier
        self.assertEqual(user.name, self.NAME)

        content['name'] = self.NAME_OTHER
        request = self.factory.post(url, content)
        response = self.as_view(request, view, view_actions)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        tokens = UserToken.objects.filter(user=user)
        self.assertEqual(len(tokens), 1)
        self.assertNotEqual(identifier, tokens[0].identifier)
        self.assertEqual(user.name, self.NAME_OTHER)

        user.delete()

    @mock.patch('customers.models.User.login')
    def test_login_demo(self, mock_login):
        url = reverse('customers:user-login')

        content = {
            'phone': DEMO_PHONE,
            'pin': self.PIN,
            'token': {
                'device': self.DEVICE,
                'service': BareDevice.APNS,
                'registration_id': self.REGISTRATION_ID
            }
        }

        view = views.UserViewSet
        view_actions = {
            'post': 'login'
        }

        # Demo account is only allowed when it's in the database
        request = self.factory.post(url, content)
        response = self.as_view(request, view, view_actions)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
        heart_url = reverse('customers:store-heart', kwargs=reverse_kwargs)
        unheart_url = reverse('customers:store-unheart', kwargs=reverse_kwargs)

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
        url = reverse('customers:user-token')

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

        self.usertoken.service = BareDevice.APNS
        self.usertoken.save()
        content['service'] = BareDevice.GCM

        request = self.factory.patch(url, content)
        response = self.authenticate_request(
            request, views.UserViewSet, view_actions=view_actions_patch)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.usertoken.refresh_from_db()
        self.assertEqual(self.usertoken.registration_id, content['registration_id'])
        self.assertEqual(self.usertoken.service, content['service'])

        self.usertoken.service = BareDevice.APNS
        self.usertoken.save()

        request = self.factory.put(url, content)
        response = self.authenticate_request(
            request, views.UserViewSet, view_actions=view_actions_put)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.usertoken.refresh_from_db()
        self.assertEqual(self.usertoken.registration_id, content['registration_id'])
        self.assertEqual(self.usertoken.service, content['service'])
