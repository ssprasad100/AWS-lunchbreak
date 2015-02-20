from business.models import Staff, Employee
from business.serializers import StaffSerializer, EmployeeSerializer
from rest_framework import generics


class StaffListView(generics.ListAPIView):
    '''
    List the staff.
    '''

    serializer_class = StaffSerializer

    def get_queryset(self):
        if 'id' in self.kwargs:
            return Staff.objects.filter(id=self.kwargs['id'])
        return Staff.objects.all()


class EmployeeListView(generics.ListAPIView):
    '''
    List the employees.
    '''

    serializer_class = EmployeeSerializer

    def get_queryset(self):
        if 'id' in self.kwargs:
            return Employee.objects.filter(id=self.kwargs['id'])
        return Employee.objects.all()
