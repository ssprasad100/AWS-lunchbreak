from __future__ import unicode_literals

import collections
import copy

from django.conf import settings
from django.contrib.auth import login, logout
from django.core.mail import BadHeaderError, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.shortcuts import HttpResponseRedirect, render
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View
from django.views.generic.base import RedirectView, TemplateResponseMixin

from .forms import CustomAuthenticationForm, TrialForm

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
        cls.context = self.update_context()
        return self

    @classmethod
    def update(cls, default, new):
        for key, value in new.iteritems():
            if isinstance(value, collections.Mapping):
                default[key] = cls.update(
                    default.get(
                        key, {}
                    ),
                    value
                )
            else:
                default[key] = new[key]
        return default

    @classmethod
    def update_context(cls):
        context = {}

        for base in cls.__bases__:
            if hasattr(base, 'update_context'):
                cls.update(
                    context,
                    base.update_context()
                )

        if hasattr(cls, 'context') and cls.context is not None:
            cls.update(
                context,
                cls.context
            )

        return context

    def render(self, *args, **kwargs):
        return render(
            self.request,
            self.template_name,
            *args,
            **kwargs
        )

    def get(self, request, *args, **kwargs):
        return self.render(
            *args,
            context=self.context.copy(),
            **kwargs
        )


class Page(PageView):
    context = {
        'title': _('Lunchbreak'),
        'description': [
            _('This is a description.'),
        ],

        'menu': {
            'background': 'transparent',
            'links': [
                {
                    'title': _('Home'),
                    'url': 'frontend-business',
                },
                {
                    'title': _('Pricing'),
                    'url': 'frontend-pricing',
                },
                {
                    'title': _('Login'),
                    'url': 'frontend-login',
                    'authentication': False
                },
                {
                    'title': _('Logout'),
                    'url': 'frontend-logout',
                    'authentication': True
                },
                {
                    'title': _('Free trial'),
                    'url': 'frontend-trial',
                },
            ]
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
                'url': 'frontend-terms',
            }
        ]
    }


class BusinessPage(Page):
    template_name = 'pages/business.html'
    context = {
        'header': {
            'background': 'business',

            'web_switch': {
                'title': _('Customers'),
                'url': 'frontend-customers',
            },

            'menu': True,

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
                    'url': 'frontend-trial',
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
            'title': _('Transparent pricing'),
            'subtitle': _('Free trial, no hidden costs and no commitments.'),
            'buttons': [
                {
                    'title': _('Explore options'),
                    'url': 'frontend-pricing',
                }, {
                    'title': _('Get started'),
                    'url': 'frontend-trial',
                    'classes': [
                        'red'
                    ]
                }
            ]
        }
    }


class CustomersPage(Page):
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


class PricingPage(Page):
    template_name = 'pages/pricing.html'
    context = {
        'title': _('Lunchbreak: Pricing'),
        'description': _('Start receiving orders online via Lunchbreak now for free!'),

        'menu': {
            'background': 'white'
        },

        'pricing': {
            'title': _('Pricing'),
            'subtitle': _('Try Lunchbreak for free'),
            'plans': [
                {
                    'title': _('Featured plan'),
                    'description': _('1 month trial'),
                    'checkboxes': [
                        _('Free installation'),
                        _('Edit your offerings on the fly'),
                        _('Receive online orders immediately'),
                        _('Realtime customer analysis')
                    ],
                    'button': {
                        'url': 'frontend-trial',
                        'text': _('Free trial')
                    }
                }
            ]
        }
    }


class TrialPage(Page):
    template_name = 'pages/trial.html'
    context = {
        'title': _('Lunchbreak: Free trial'),
        'description': _('Try Lunchbreak for free with the free trial and '
                         'start accepting orders online!'),

        'menu': {
            'background': 'white'
        },

        'trial': {
            'title': _('Signup'),
            'description': _('Enter your details below and we will set you up '
                             'with Lunchbreak as soon as possible!'),
            'form': TrialForm(),
            'submit': _('Signup'),
            'error': {
                'title': _('Slight problem!'),
                'description': _('Check for any errors in your entry and try again.'),
            },

            'success': {
                'title': _('Welcome!'),
                'description': _('We will get in touch as soon as possible. '
                                 'Got any questions in the meantime? You can '
                                 'reach out to us at hello@cloock.be or '
                                 '+32 479 42 78 66.'),
            }
        }
    }

    def get(self, request, *args, **kwargs):
        self.context['trial']['form'] = TrialForm()
        return super(TrialPage, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = copy.deepcopy(self.context)
        form = TrialForm(
            request.POST
        )

        if form.is_valid():
            context['trial']['valid'] = True

            company = request.POST['company']
            template_context = {
                'company': company,
                'country': request.POST['country'],
                'city': request.POST['city'],
                'email': request.POST['email'],
                'phone': request.POST['phone'],
            }

            subject = '{company} wil Lunchbreak uitproberen'.format(
                company=company.capitalize()
            )
            to_email = 'hello@cloock.be'
            plaintext = render_to_string('email/trial.txt', template_context)

            msg = EmailMultiAlternatives(
                subject,
                plaintext,
                settings.EMAIL_FROM,
                [to_email]
            )

            try:
                msg.send()
            except BadHeaderError:
                pass
        else:
            context['trial']['form'] = form

        return self.render(
            context=context,
            **kwargs
        )


class TermsPage(Page):
    template_name = 'pages/terms.html'
    context = {

    }


class LogoutView(RedirectView):
    permanent = True
    query_string = False
    pattern_name = 'frontend-business'

    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        return super(LogoutView, self).get_redirect_url(*args, **kwargs)


class LoginPage(Page):
    template_name = 'pages/login.html'
    context = {
        'title': _('Lunchbreak: Login'),
        'description': _('Login to your Lunchbreak business account.'),

        'menu': {
            'background': 'white'
        },

        'login': {
            'title': _('Login'),
            'description': _('Please login with your store\'s credentials.'),

            'error': {
                'title': _('Slight problem!'),
                'description': _('Check for any errors in your entry and try again.'),
            },

            'submit': _('Login'),

            'form': CustomAuthenticationForm()
        }
    }

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('frontend-business'))

        self.context['login']['form'] = CustomAuthenticationForm()
        return super(LoginPage, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('frontend-business'))

        form = CustomAuthenticationForm(
            data=request.POST
        )

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return HttpResponseRedirect('frontend-business')

        self.context['login']['form'] = form
        return super(LoginPage, self).get(request, *args, **kwargs)
