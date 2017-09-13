from customers.tests import CustomersTestCase
from push_notifications.models import BareDevice

from ..models import Employee, EmployeeToken, Staff


class BusinessTestCase(CustomersTestCase):

    def setUp(self):
        super().setUp()

        self.owner = Employee.objects.create(
            staff=self.staff,
            name='Owner',
            owner=True
        )
        self.employee = Employee.objects.create(
            staff=self.staff,
            name='Employee',
        )

        self.ownertoken = EmployeeToken.objects.create(
            identifier='something',
            device='something',
            employee=self.owner,
            registration_id='something',
            service=BareDevice.APNS
        )

        self.other_staff = Staff(
            store=self.other_store,
            email=self.EMAIL_OTHER,
            first_name='Other',
            last_name='Staff'
        )
        self.other_staff.set_password(self.PASSWORD)
        self.other_staff.save()

        self.other_owner = Employee.objects.create(
            staff=self.other_staff,
            name='Owner',
            owner=True
        )
        self.other_employee = Employee.objects.create(
            staff=self.other_staff,
            name='Employee'
        )

        self.other_owner = Employee.objects.create(
            name=self.NAME_USER,
            staff=self.other_staff,
            owner=True
        )
