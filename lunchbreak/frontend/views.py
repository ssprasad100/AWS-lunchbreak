import json

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin

language_flags = {
    'nl-be': 'be',
    'en': 'eu',
    'fr': 'fr',
    'en-us': 'us',
}


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
        'description': [
            _('This is a description.'),
        ],

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
        },

        'languages': {
            language[0]: {
                'name': language[1],
                'image': 'img/icons/flags/{code}.png'.format(
                    code=language_flags[language[0]]
                ),
                'url': '',
            } for language in settings.LANGUAGES
        },

        'footer': [
            {
                'title': _('Terms'),
                'url': _(''),
            }
        ]
    }


class BusinessPage(BasePage):
    template_name = 'pages/business.html'
    context = {
        'header': {
            'background': 'business',

            'web_switch': {
                'title': _('Customers'),
                'url': 'frontend-customers',
            },

            'title': _('Lunchbreak'),
            'description': [
                _('Online ordering tailored to your business')
            ],

            'buttons': [
                {
                    'title': _('Learn more'),
                    'id': 'advantages',
                    'classes': [
                        'white'
                    ]
                },
                {
                    'title': _('Free trial'),
                    'id': 'TODO CHANGE TO URL TRIAL',
                    'classes': [
                        'red'
                    ]
                }
            ],
        },
        'advantages': {
            'id': 'advantages',
            'title': _('Why Lunchbreak?'),
            'slideshow': [
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
            'slideshow': [
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
            'description': _('Add, remove or edit your offerings on the fly. '
                             'Have a special dish every week? No problem. We '
                             'even add your whole offerings when joining '
                             'Lunchbreak for free!'),
            'slideshow': [
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
        },
        'customers': {
            'title': _('Customer benefits'),
            #  'subtitle': _('Test subtitle'),
            'checkboxes': [
                _('Order anywhere at anytime!'),
                _('Customise their orders'),
                _('Notified when order is ready'),
                _('No more queues')
            ],
            'slideshow': [
                {
                    'image': _('img/screenshots/en/customers/overview.jpg'),
                    'alt': _('Store selection'),
                },
                {
                    'image': _('img/screenshots/en/customers/store.jpg'),
                    'alt': _('Store'),
                },
                {
                    'image': _('img/screenshots/en/customers/ingredients.png'),
                    'alt': _('Select ingredients'),
                },
                {
                    'image': _('img/screenshots/en/customers/cart.png'),
                    'alt': _('Cart'),
                },
                {
                    'image': _('img/screenshots/en/customers/pickup.png'),
                    'alt': _('Select time of pickup'),
                },
                {
                    'image': _('img/screenshots/en/customers/notification.png'),
                    'alt': _('Notification'),
                },
            ]
        },
        'faq': {
            'title': _('Frequently asked questions'),
            'qa': [
                {
                    'question': _('What if an order is not picked up?'),
                    'answer': _('Users are required to login using their '
                                'phone number. We always know with certainty '
                                'the phone number of the user in question. '
                                'Fake orders are less probable this way '
                                'because our users know we that have their '
                                'phone number.')
                },
                {
                    'question': _('Can I specify how much in advance an order '
                                  'needs to be placed?'),
                    'answer': _('Certainly! That and a lot more can be easily '
                                'customised with the iPad app. Are you a '
                                'bakery and want people to order a day in '
                                'advance for certain products? We accounted '
                                'for that too.')
                },
                {
                    'question': _('Will this work for my <insert business type here>?'),
                    'answer': _('We designed Lunchbreak in order to work for '
                                'every single type of store on the planet! '
                                'Contact us if we missed something and we '
                                'wil gladly look into it!')
                },
                {
                    'question': _('Do I have to add the offerings myself?'),
                    'answer': _('You can, but at the time we offer to add '
                                'it for you for free at the time of '
                                'installation. We do recommend for you to give '
                                'it a shot in order to get familiar with Lunchbreak.')
                },
                {
                    'question': _('Can I disable online payments?'),
                    'answer': _('Of course, Lunchbreak is tailored to your business!'),
                },
                {
                    'question': _('What devices does Lunchbreak support?'),
                    'answer': _('Your users can use the iOS or Android app. '
                                'The app for your store is currently only '
                                'available for Apple iPad devices.')
                }
            ]
        },
        'next': {
            'title': _('Simple and fast food ordering'),
            'subtitle': _('Free trial, no hidden costs and no commitments.'),
            'buttons': [
                {
                    'title': _('Workflow'),
                    'url': _(''),
                }, {
                    'title': _('Get started'),
                    'url': _(''),
                    'classes': [
                        'red'
                    ]
                }
            ]
        }
    }


class CustomersPage(BasePage):
    template_name = 'pages/customers.html'
    context = {
        'header': {
            'web_switch': {
                'title': _('Business'),
                'url': 'frontend-business',
            },

            'title': _('Lunchbreak'),
            'description': [
                _('Personalised online food ordering'),
                _('Order anywhere, anytime using your smartphone'),
            ],

            'buttons': [
                {
                    'title': _('Learn more'),
                    'id': 'advantages',
                    'classes': [
                        'white'
                    ]
                },
                {
                    'title': _('Download'),
                    'id': 'download',
                    'classes': [
                        'red'
                    ]
                }
            ],
        },
        'advantages': {
            'id': 'advantages',
            'title': _('Easy for everyone'),
            'slideshow': [
                {
                    'title': _('Save time'),
                    'description': _('Order in advance and skip the queue '
                                     'because your order is already waiting.'),
                    'image': 'img/advantages/clock.png',
                },
                {
                    'title': _('Order anywhere, anytime'),
                    'description': _('Order during class, at your job or in '
                                     'your sofa, anytime and wherever you are.'),
                    'image': 'img/advantages/map.png',
                },
                {
                    'title': _('Easy pickup'),
                    'description': _('Receive a notification when your order '
                                     'is ready and lose not time picking your '
                                     'order up.'),
                    'image': 'img/advantages/bike.png',
                },
                {
                    'title': _('Secure and no password'),
                    'description': _('Log in once using your mobile phone, '
                                     'that\'s it! No more passwords!'),
                    'image': 'img/advantages/lock.png',
                },
                {
                    'title': _('Always in stock'),
                    'description': _('Pickup at anytime, we have already put '
                                     'it aside for you. No hassle.'),
                    'image': 'img/advantages/list.png',
                },
                {
                    'title': _('Local quality'),
                    'description': _('Solely quality nearby stores are '
                                     'displayed in the app. Only the best.'),
                    'image': 'img/advantages/store.png',
                },
            ]
        },
        'features': {
            'title': _('App features'),
            'checkboxes': [
                _('No passwords'),
                _('One-time login'),
                _('Order personalisation'),
                _('Piece of cake, literally!'),
                _('Get notified of your order'),
            ],
            'video': {
                'poster': _('img/video/en/iphone/poster.png'),
                'placeholder': {
                    'image': _('img/video/en/iphone/poster.png'),
                    'alt': _('Lunchbreak home screen'),
                },
                'sources': [
                    {
                        'src': _('img/video/en/iphone/video.mp4'),
                        'type': 'video/mp4'
                    }
                ]
            }
        },
        'steps': {
            'title': _('Ordering process'),
            'one': {
                'small': _('Store'),
                'big': _('Selection')
            },
            'two': {
                'small': _('Order'),
                'big': _('Placement')
            },
            'three': {
                'small': _('Pickup'),
                'big': _('Planning')
            },
            'four': {
                'small': _('Order'),
                'big': _('Pickup')
            },
        },

        'download': {
            'id': 'download',
            'title': _('Download'),
            'text': _('Available for free in the Apple App Store and in the '
                      'Google Play Store.'),
            'ios': {
                'image': _('img/stores/nl-be/ios.png'),
                'alt': _('Apple App Store'),
            },
            'android': {
                'image': _('img/stores/nl-be/android.png'),
                'alt': _('Google Play Store'),
            },
        },


        'last': {
            'follow': {
                'facebook': {
                    'title': 'Facebook',
                    'url': 'https://www.facebook.com/lunchbreakapp'
                },
                'twitter': {
                    'title': 'Twitter',
                    'url': 'https://twitter.com/LunchbreakApp',
                    'username': '@LunchbreakApp',
                    'image': 'img/social/twitter-heading.png',
                },
                'text': {
                    'follow': _('Follow us on '),
                    'and': _('and'),
                }
            },
            'subscribe': {
                'title': _('Newsletter'),
                'text': _('Want to know when Lunchbreak opens a store near '
                          'you? Want to be the first one to get to know the '
                          'new features of Lunchbreak. Signup for the '
                          'newsletter and be part of the exclusive club!'),
                'email': _('john@example.com'),
                'button': _('Subscribe'),
            },
        },
    }
