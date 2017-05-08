from uuid import uuid4

from business.models import Staff
from django_gocardless.models import Merchant as GoCardlessMerchant
from django_sms.models import Phone
from lunch.tests import LunchTestCase
from payconiq.models import Merchant as PayconiqMerchant
from push_notifications.models import SERVICE_APNS

from ..models import User, UserToken


class CustomersTestCase(LunchTestCase):

    PHONE_USER = '+32472907604'
    NAME_USER = 'Meneer Aardappel'
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

    def setUp(self):
        super().setUp()

        self.phone = Phone.objects.create(
            phone=self.PHONE_USER,
            confirmed_at=self.midday._datetime
        )
        self.other_phone = Phone.objects.create(
            phone=self.VALID_PHONE2,
            confirmed_at=self.midday._datetime
        )

        self.user = User.objects.create(
            phone=self.phone,
            name=self.NAME_USER
        )

        self.other_user = User.objects.create(
            phone=self.other_phone,
            name=self.NAME_OTHER
        )

        self.usertoken = UserToken.objects.create(
            identifier='something',
            device='something',
            user=self.user,
            registration_id='something',
            service=SERVICE_APNS
        )
        self.other_usertoken = UserToken.objects.create(
            identifier='something',
            device='something',
            user=self.other_user,
            registration_id='something',
            service=SERVICE_APNS
        )

        self.gocardless = GoCardlessMerchant.objects.create()
        self.payconiq = PayconiqMerchant.objects.create(
            remote_id='12345',
            access_token='secret',
            widget_token=uuid4()
        )
        self.staff = Staff.objects.create(
            store=self.store,
            email=self.EMAIL,
            gocardless=self.gocardless,
            payconiq=self.payconiq
        )
