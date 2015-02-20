from django.conf.urls import patterns, url
from business import views

urlpatterns = patterns('',
    url(r'staff/$', views.StaffListView.as_view()),
    url(r'staff/(?P<id>\d+)/$', views.StaffListView.as_view()),
    url(r'staff/reset/request/(?P<email>.+)/$', views.StaffRequestReset.as_view()),
    url(r'staff/reset/(?P<email>.+)/(?P<passwordReset>.+)/$', views.StaffResetView.as_view()),

    url(r'employee/$', views.EmployeeListView.as_view()),
    url(r'employee/(?P<id>\d+)/$', views.EmployeeListView.as_view()),
)
