from business.authentication import StaffAuthentication
from business.models import Employee, Staff
from business.serializers import EmployeeSerializer, StaffSerializer
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

    authentication_classes = (StaffAuthentication,)
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        if 'id' in self.kwargs:
            return Employee.objects.filter(id=self.kwargs['id'], staff=self.request.user)
        return Employee.objects.filter(staff=self.request.user)
