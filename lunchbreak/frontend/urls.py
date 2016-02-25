from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(
        r'^customers$',
        views.CustomersPage.as_view(),
        name='frontend-customers'
    ),
    url(
        r'^pricing$',
        views.PricingPage.as_view(),
        name='frontend-pricing'
    ),
    url(
        r'^trial$',
        views.TrialPage.as_view(),
        name='frontend-trial'
    ),
    url(
        r'^terms$',
        views.TermsPage.as_view(),
        name='frontend-terms'
    ),
    url(
        r'^',
        views.BusinessPage.as_view(),
        name='frontend-business'
    ),
)
