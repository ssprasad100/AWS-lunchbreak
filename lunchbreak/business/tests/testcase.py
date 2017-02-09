from customers.tests import CustomersTestCase

from ..models import Employee, Staff


class BusinessTestCase(CustomersTestCase):

    def setUp(self):
        super().setUp()

        self.staff = Staff.objects.create(
            store=self.store,
            email=self.EMAIL
        )

        self.owner = Employee.objects.create(
            staff=self.staff,
            name='Owner',
            owner=True
        )
        self.employee = Employee.objects.create(
            staff=self.staff,
            name='Employee'
        )

        self.other_staff = Staff.objects.create(
            store=self.other_store,
            email=self.EMAIL_OTHER
        )

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
