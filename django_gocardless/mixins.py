
import gocardless_pro
from django.conf import settings
from django.db import models
from django.utils.functional import cached_property

from .config import CLIENT_PROPERTIES


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
        access_token = self.merchant.access_token \
            if self.merchant is not None \
            else settings.GOCARDLESS['access_token']

        return gocardless_pro.Client(
            access_token=access_token,
            environment=settings.GOCARDLESS['environment']
        )

    @cached_property
    def api(self):
        class_name = self.__class__.__name__
        return getattr(self.client, CLIENT_PROPERTIES[class_name])

    def from_resource(self, resource):
        from .utils import model_from_links

        fields = self.__class__._meta.get_fields()

        for field in fields:
            value = '' if issubclass(field.__class__, models.CharField) else None
            temp = None

            if hasattr(resource, field.name):
                temp = getattr(resource, field.name)
            elif hasattr(resource, 'links') and hasattr(resource.links, field.name):
                temp = model_from_links(resource.links, field.name)

            value = temp if temp is not None else value
            setattr(self, field.name, value)

    def from_api(self, method, *args, **kwargs):
        resource = method(
            *args,
            **kwargs
        )
        self.from_resource(resource)

    def fetch(self, *args, **kwargs):
        self.from_api(
            self.api.get,
            self.id
        )
        self.save(*args, **kwargs)


class GCCreateMixin(GCCacheMixin):

    '''
    Models that are not only cached for ease of use, but should be able to be
    created from this server using the GoCardless API.
    '''

    create_fields = {}

    @classmethod
    def check_fields(cls, fields, given):
        '''
        Argument 'fields' example:
        {
            'required': [
                'address_line1',
                'city',
                'company_name',
                'country_code',
                'postal_code',
            ],
            'optional': [
                'region',
            ],
        }
        '''

        if 'required' not in fields and 'optional' not in fields:
            raise NotImplementedError(
                ('{cls}.create_fields needs to be implemented and the '
                    '\'required\' or \'optional\' keys must be set.').format(
                    cls=cls.__name__
                )
            )

        required_fields = fields['required'] if 'required' in fields else []

        for required_field in required_fields:
            if required_field not in given:
                raise ValueError(
                    'The following keys are required: {keys}'.format(
                        keys=','.join(required_fields)
                    )
                )

        allowed_fields = required_fields +\
            fields['optional']\
            if 'optional' in fields\
            else required_fields

        for field_given in given.iterkeys():
            if field_given not in allowed_fields:
                raise ValueError(
                    ('The field \'{field_given}\' is not allowed to be updated,'
                     'these are: {allowed_fields}').format(
                        field_given=field_given,
                        allowed_fields=allowed_fields
                    )
                )

    @classmethod
    def create(cls, given, instance=None, *args, **kwargs):
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
