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
            'background': 'transparent',
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
        },

        'ipad': {
            'width': 1284,
            'height': 865
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
        },
        'orders': {
            'title': _('Online orders'),
            'description': _('Receive orders right on your iPad. Keep track '
                'of orders currently in progress, confirm orders and correct '
                'the final cost if necessary.'),
            'items': [
                {
                    'image': {
                        'without': _('img/screenshots/en/orders/without1.png'),
                        'with': _('img/screenshots/en/orders/with1.png')
                    },
                    'alt': _('Online order on your iPad')
                },
                {
                    'image': {
                        'without': _('img/screenshots/en/orders/without2.png'),
                        'with': _('img/screenshots/en/orders/with2.png')
                    },
                    'alt': _('Prepare orders')
                },
                {
                    'image': {
                        'without': _('img/screenshots/en/orders/without3.png'),
                        'with': _('img/screenshots/en/orders/with3.png')
                    },
                    'alt': _('Confirm orders')
                },
            ]
        },
        'offerings': {
            'title': _('Manage offerings'),
            'description': _('Add, remove or edit your offerings on the fly. Have a special dish every week? No problem. We even add your whole offerings when joining Lunchbreak for free!'),
            'items': [
                {
                    'image': {
                        'without': _('img/screenshots/en/offerings/without1.png'),
                        'with': _('img/screenshots/en/offerings/with1.png')
                    },
                    'alt': _('Manage categories on your iPad')
                },
                {
                    'image': {
                        'without': _('img/screenshots/en/offerings/without2.png'),
                        'with': _('img/screenshots/en/offerings/with2.png')
                    },
                    'alt': _('Manage offerings on your iPad')
                },
                {
                    'image': {
                        'without': _('img/screenshots/en/offerings/without3.png'),
                        'with': _('img/screenshots/en/offerings/with3.png')
                    },
                    'alt': _('Edit products on your iPad')
                },
            ]
        }



    }
