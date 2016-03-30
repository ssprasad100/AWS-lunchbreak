import copy

import gocardless_pro
import six
from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from gocardless_pro.errors import GoCardlessProError

from .config import CLIENT_PROPERTIES
from .exceptions import DjangoGoCardlessException
from .utils import field_default, model_from_links


class GCCacheMixin(object):

    '''
    Models that are cached for ease of use. These can be out of date with the
    GoCardless database and should therefore provide a way to sync with the
    GoCardless database. The `id` of the model should always be in sync if in
    the GoCardless database.
    '''

    @cached_property
    def merchant(self):
        raise NotImplementedError(
            '{cls} needs to implement the merchant property.'.format(
                cls=self.__class__.__name__
            )
        )

    @cached_property
    def client(self):
        '''
        Use a merchant's access token if available, else use the access token
        provided in the settings and return the GoCardless client.
        '''

        access_token = self.merchant.access_token \
            if self.merchant is not None \
            else settings.GOCARDLESS['access_token']

        return gocardless_pro.Client(
            access_token=access_token,
            environment=settings.GOCARDLESS['environment']
        )

    @classmethod
    def api_from_client(cls, client):
        '''Appropriate GoCardless Service for model.'''

        class_name = cls.__name__
        return getattr(client, CLIENT_PROPERTIES[class_name])

    @cached_property
    def api(self):
        return self.api_from_client(self.client)

    @staticmethod
    def field_default(field):
        cls = field.__class__

        default = getattr(field, 'default', None)
        default = None if default is models.NOT_PROVIDED else default

        if (default is None and
            (issubclass(cls, models.CharField) or
             issubclass(cls, models.TextField))):
            return ''
        return default

    def from_resource(self, resource, client=None):
        '''
        Set a GCCacheMixin's attributes based on a GoCardless resource.
        '''

        client = self.client if client is None else client
        fields = self.__class__._meta.get_fields()

        for field in fields:
            if not issubclass(field.__class__, models.fields.Field):
                continue

            value = field_default(field)
            temp = None
            is_resource_field = False

            if hasattr(resource, field.name):
                temp = getattr(resource, field.name)
                is_resource_field = True
            elif hasattr(resource, 'links') and hasattr(resource.links, field.name):
                temp = model_from_links(resource.links, field.name, client)
                is_resource_field = True

            if is_resource_field:
                value = temp if temp is not None else value
                setattr(self, field.name, value)

    def from_api(self, method, *args, **kwargs):
        '''
        Shorthand for `self.from_resource(resource)` with `resource` generated
        from the given GoCardless Service method.
        '''

        client = kwargs.pop('client', None)

        try:
            resource = method(
                *args,
                **kwargs
            )
        except GoCardlessProError as e:
            raise DjangoGoCardlessException.from_gocardless_exception(e)
        client = self.client if client is None else client
        self.from_resource(resource, client)

    @classmethod
    def fetch(cls, instance=None, where=None, client=None, *args, **kwargs):
        '''
        Fetch information from the GoCardless API, update and save the instance.
        '''
        if instance is None:
            if where is None:
                raise ValueError('`instance` and `where` cannot both be None.')
            else:
                instance = cls(
                    **where
                )

        client = instance.client if client is None else client
        api = cls.api_from_client(client)

        instance.from_api(
            api.get,
            instance.id,
            client=client
        )
        instance.save(*args, **kwargs)

        return instance


class GCCreateMixin(GCCacheMixin):

    '''
    Models that are not only cached for ease of use, but should be able to be
    created from this server using the GoCardless API.
    '''

    create_fields = {}

    @classmethod
    def check_required(cls, required_fields, given):
        for required_field in required_fields:
            if isinstance(required_field, six.string_types):
                if required_field not in given:
                    break
            elif isinstance(required_field, dict):
                raise_error = False

                for field, field_list in required_field.iteritems():
                    if field not in given:
                        raise_error = True
                        break
                    cls.check_required(
                        field_list,
                        given[field]
                    )
                if raise_error:
                    break
            else:
                break
        else:  # No breaks means everything is ok
            return
        raise ValueError(
            'These fields are required: {required_fields}.'.format(
                required_fields=required_fields
            )
        )

    @classmethod
    def check_optional(cls, optional_fields, given):
        for given_field, given_value in given.iteritems():
            for optional_field in optional_fields:
                if isinstance(optional_field, six.string_types)\
                        and optional_field == given_field:
                    break
                elif isinstance(optional_field, dict):
                    for field, field_list in optional_field:
                        if field not in given:
                            break
                        cls.check_optional(
                            field_list,
                            given[field]
                        )
            else:
                raise ValueError(
                    'The field \'{given_field}\' is not allowed.'.format(
                        given_field=given_field
                    )
                )

    @classmethod
    def check_fields(cls, fields, given):
        '''
        Check if the fields given are viable for the fields that are required
        or optional.

        Used in GCCreateMixin.create and GCCreateUpdateMixin.update

        `fields` example:

            {
                'required': [
                    'address_line1',
                    'city',
                    'company_name',
                    'country_code',
                    'postal_code',
                    {
                        'links': [
                            'mandate',
                        ],
                    },
                ],
                'optional': [
                    'region',
                ],
            }

            {
                'address_line1': '',
                'city': '',
                'company_name': '',
                'country_code': '',
                'postal_code': '',
                'links': {
                    'mandate': '',
                },
            }
        '''

        if 'required' not in fields or 'optional' not in fields:
            raise NotImplementedError(
                '`fields` needs to have the key \'required\' or \'optional\' set.'
            )

        required_fields = fields['required'] if 'required' in fields else []

        cls.check_required(required_fields, given)

        given_copy = copy.copy(given)
        for required_field in required_fields:
            if isinstance(required_field, six.string_types):
                del given_copy[required_field]
            elif isinstance(required_field, dict):
                for required_f in required_field:
                    del given_copy[required_f]

        optional_fields = fields['optional'] if 'optional' in fields else []

        cls.check_optional(optional_fields, given_copy)

    @classmethod
    def create(cls, given, instance=None, check=True, *args, **kwargs):
        '''
        Create a resource on the GoCardless servers.
        '''

        if check:
            cls.check_fields(
                cls.create_fields,
                given
            )

        instance = cls() if instance is None else instance
        instance.from_api(
            instance.api.create,
            params=given
        )
        instance.save(*args, **kwargs)

        return instance


class GCCreateUpdateMixin(GCCreateMixin):

    '''
    Models that are not only cached for ease of use, but should be able to be
    created and updated from this server using the GoCardless API.
    '''

    update_fields = {}

    def update(self, given, *args, **kwargs):
        '''
        Update a resource on the GoCardless servers.
        '''

        self.check_fields(
            self.create_fields,
            given
        )

        self.from_api(
            self.api.update,
            self.id,
            params=given
        )
        self.save(*args, **kwargs)
