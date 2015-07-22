#!/usr/bin/env python
import inspect
import os
import copy
import json

from configurations import importer
from django.apps import apps
from django.conf import settings
from django.db.models import fields as modelFields
from Lunchbreak.config import Base

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lunchbreak.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Development')

importer.install()
apps.populate(settings.INSTALLED_APPS)

from rest_framework.serializers import ModelSerializer
from rest_framework import fields, relations

import business.serializers as businessSerializers
import customers.serializers as customersSerializers
import lunch.serializers as lunchSerializers

serializerModules = {
    'lunch': lunchSerializers,
    'customers': customersSerializers,
    'business': businessSerializers
}


def pretty(obj, indent=0):
    if isinstance(obj, list):
        for value in obj:
            pretty(value, indent=indent)
    elif not isinstance(obj, str) and hasattr(obj, 'iteritems'):
        for key, value in obj.iteritems():
            pretty(key, indent=indent)
            pretty(value, indent=indent + 1)
    elif inspect.isclass(obj) or isinstance(obj, Schema):
        pretty(str(obj), indent=indent)
        pretty(obj.__dict__, indent=indent + 1)
    else:
        print '\t' * indent + str(obj)


class SchemaEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Schema):
            return super(SchemaEncoder, self).default(obj)

        return obj.representation()


class Schema(object):
    def __init__(self):
        self.displayName = None
        self.description = None

        self.type = None
        self.enum = []
        self.pattern = None

        self.minLength = None
        self.maxLength = None

        self.minimum = None
        self.maximum = None

        self.example = None
        self.repeat = None
        self.required = None
        self.default = None

        self.properties = []

    def representation(self):
        result = {}
        if self.displayName is not None:
            result['displayName'] = self.displayName
        if self.description is not None:
            result['description'] = self.description

        if self.type is not None:
            result['type'] = self.type
        if self.enum is not None and len(self.enum) > 0:
            result['enum'] = self.enum
        if self.pattern is not None:
            result['pattern'] = self.pattern

        if self.minLength is not None:
            result['minLength'] = self.minLength
        if self.maxLength is not None:
            result['maxLength'] = self.maxLength

        if self.minimum is not None:
            result['minimum'] = self.minimum
        if self.maximum is not None:
            result['maximum'] = self.maximum

        if self.example is not None:
            result['example'] = self.example
        if self.repeat is not None:
            result['repeat'] = self.repeat
        if self.required is not None:
            result['required'] = self.required
        if self.default is not None:
            result['default'] = self.default

        if self.properties is not None and len(self.properties) > 0:
            result['properties'] = self.properties

        return result

    @staticmethod
    def getSchemas(obj, read=True, write=True, displayName=None, modelField=None):
        if issubclass(obj.__class__, fields.Field):
            schema = Schema()

            schema.displayName = displayName
            schema.description = obj.label

            schema.example = None
            schema.required = obj.required
            schema.default = None if obj.default is fields.empty else str(obj.default)

            if issubclass(obj.__class__, ModelSerializer):
                if schema.displayName is None:
                    schema.displayName = obj.__class__.__name__.replace('Serializer', '')
                if obj.__doc__ is not None:
                    schema.description = obj.__doc__

                schema.type = 'object'

                meta = obj.Meta

                readSchema = copy.deepcopy(schema)
                writeSchema = schema

                try:
                    for fieldName, field in obj.get_fields().iteritems():
                        if issubclass(field.__class__, fields.Field):
                            read_only = getattr(field, 'read_only')
                            write_only = getattr(field, 'write_only')
                            neither = not read_only and not write_only

                            propertySchema = Schema.getSchemas(field, read=read_only, write=write_only, displayName=fieldName, modelField=getattr(meta.model, fieldName, None))

                            if read and (read_only or neither):
                                readSchema.properties.append(propertySchema)
                            elif write and (write_only or neither):
                                writeSchema.properties.append(propertySchema)

                    if read and write:
                        return [readSchema, writeSchema]
                    elif read:
                        return readSchema
                    else:
                        return writeSchema
                except ValueError:
                    pass

            else:
                schema.minLength = getattr(obj, 'min_length', None)
                schema.maxLength = getattr(obj, 'max_length', None)

                schema.minimum = getattr(obj, 'min_value', None)
                schema.maximum = getattr(obj, 'max_value', None)

                if obj.__class__ in [fields.BooleanField, fields.NullBooleanField]:
                    schema.type = 'boolean'
                elif obj.__class__ is fields.IntegerField:
                    schema.type = 'integer'
                elif obj.__class__ in [fields.FloatField, fields.DecimalField]:
                    schema.type = 'number'
                elif obj.__class__ in [fields.DateTimeField, fields.DateField, fields.TimeField, fields.DurationField]:
                    schema.type = 'date'
                    if obj.__class__ is fields.DateTimeField:
                        schema.pattern = Base.DATETIME_FORMAT
                    elif obj.__class__ is fields.DateField:
                        schema.pattern = Base.DATE_FORMAT
                    else:
                        schema.pattern = Base.TIME_FORMAT
                elif obj.__class__ in [fields.ChoiceField, fields.MultipleChoiceField]:
                    # RAML requires enums to have the type 'string'
                    schema.type = 'string'
                    schema.enum = [a for a in obj.choices]
                elif issubclass(obj.__class__, fields.FileField):
                    schema.type = 'file'
                elif obj.__class__ is relations.PrimaryKeyRelatedField and modelField is not None:
                    pkField = modelField.field.model._meta.pk.__class__
                    if issubclass(pkField, modelFields.IntegerField) or pkField in [modelFields.AutoField, modelFields.BinaryField]:
                        schema.type = 'integer'
                    elif pkField in [modelFields.BooleanField, modelFields.NullBooleanField]:
                        schema.type = 'boolean'
                    elif pkField in [modelFields.DecimalField, modelFields.FloatField]:
                        schema.type = 'number'
                    elif issubclass(pkField, modelFields.DateField) or pkField in [modelFields.DurationField, modelFields.TimeField]:
                        schema.type = 'date'
                    else:
                        schema.type = 'string'
                else:
                    schema.type = 'string'

                return schema

done = False

for folder, serializerModule in serializerModules.iteritems():
    for name, obj in inspect.getmembers(serializerModule):
        if inspect.isclass(obj):
            if issubclass(obj, ModelSerializer):
                if not done:
                    schemas = Schema.getSchemas(obj())
                    #pretty(schemas)
                    #for s in schemas:
                    #    print s.representation()
                    print json.dumps(schemas, indent=4, cls=SchemaEncoder)
                    done = False
