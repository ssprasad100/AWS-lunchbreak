from django.conf.urls import patterns, url
from business import views

urlpatterns = patterns('',
    url(r'staff/$', views.StaffListView.as_view(), name='staff_list'),
    url(r'staff/(?P<id>.+)/$', views.StaffListView.as_view(), name='staff_specific'),

    url(r'employee/$', views.EmployeeListView.as_view(), name='employee_list'),
    url(r'employee/(?P<id>\d+)/$', views.EmployeeListView.as_view(), name='employee_specific'),
)
