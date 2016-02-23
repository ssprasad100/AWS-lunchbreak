from django.utils.translation import ugettext_lazy as _
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin


class PageView(View, TemplateResponseMixin):
    template_name = None
    context = {}

    def __new__(cls):
        self = super(PageView, cls).__new__(cls)
        self.update_context()
        return self

    @classmethod
    def update_context(cls):
        if not hasattr(cls, 'context') or cls.context is None:
            cls.context = {}

        for base in cls.__bases__:
            if hasattr(base, 'update_context'):
                cls.context.update(
                    base.update_context()
                )
        return cls.context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(
            context=self.context,
            **kwargs
        )


class BasePage(PageView):
    context = {
        'title': _('Lunchbreak'),
        'description': _('This is a description.'),

        'header': {
            'users': _('Users'),

            'title': _('Lunchbreak'),
            'description': _('Online ordering tailored to your business'),

            'button_info': _('Learn more'),
            'button_trial': _('Free trial'),
        },

        'menu': {
            'items': [
                {
                    'title': _('Home'),
                    'url': '',
                },
                {
                    'title': _('Workflow'),
                    'url': '',
                },
                {
                    'title': _('Pricing'),
                    'url': '',
                },
                {
                    'title': _('Free trial'),
                    'url': '',
                },
            ]
        },

        'ids': {
            'info_id': 'more-info'
        }
    }


class IndexPage(BasePage):
    template_name = 'pages/index.html'
    context = {
        'advantages': {
            'title': _('Why Lunchbreak?'),
            'items': [
                {
                    'title': _('Save time'),
                    'description': _('No need to write orders down. No need for phone calls.'),
                    'image': 'img/advantages/clock.png',
                },
                {
                    'title': _('Online payments'),
                    'description': _('Our ultra low fees are 7 times cheaper '
                                     'than the average fees in our market.'),
                    'image': 'img/advantages/creditcards.png',
                },
                {
                    'title': _('Satisfied customers'),
                    'description': _('No need to wait, they can even pay in advance!'),
                    'image': 'img/advantages/customer.png',
                },
                {
                    'title': _('Real time statistics'),
                    'description': _('Improve your store by analysing your statistics.'),
                    'image': 'img/advantages/statistics.png',
                },
            ]
        }
    }