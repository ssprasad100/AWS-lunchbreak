#!/usr/bin/env python
import inspect
import os
import copy
import json
import shutil

from configurations import importer
from django.apps import apps
from django.conf import settings
from django.db.models import fields as djangoFields
from Lunchbreak.config import Base

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lunchbreak.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Development')

importer.install()
apps.populate(settings.INSTALLED_APPS)

from rest_framework.serializers import ModelSerializer, BaseSerializer
from rest_framework import fields, relations

import business.serializers as businessSerializers
import customers.serializers as customersSerializers
import lunch.serializers as lunchSerializers

serializerModules = {
    'lunch': lunchSerializers,
    'customers': customersSerializers,
    'business': businessSerializers
}


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
    def getSchemas(obj, read=True, write=True, displayName=None, model=None):
        modelField = getattr(model, displayName, None) if displayName is not None else None

        if issubclass(obj.__class__, fields.Field):
            schema = Schema()

            schema.displayName = displayName
            schema.description = getattr(obj, 'help_text', None)
            schema.description = getattr(obj, 'label', None) if schema.description is None else schema.description

            schema.example = None
            schema.required = obj.required
            schema.default = None if obj.default is fields.empty else str(obj.default)

            if issubclass(obj.__class__, BaseSerializer):
                if schema.displayName is None:
                    schema.displayName = obj.__class__.__name__.replace('Serializer', '')
                if obj.__doc__ is not None:
                    schema.description = obj.__doc__

                schema.type = 'object'

                meta = getattr(obj, 'meta', None)
                model = getattr(meta, 'model', None) if meta is not None else None

                readSchema = copy.deepcopy(schema)
                writeSchema = schema

                try:
                    objFields = obj.get_fields() if hasattr(obj, 'get_fields') else obj.child.get_fields()
                    for fieldName, field in objFields.iteritems():
                        if issubclass(field.__class__, fields.Field):
                            read_only = getattr(field, 'read_only')
                            write_only = getattr(field, 'write_only')
                            neither = not read_only and not write_only

                            propertySchema = Schema.getSchemas(field, read=read_only, write=write_only, displayName=fieldName, model=model)

                            if read and (read_only or neither):
                                readSchema.properties.append(propertySchema)
                            if write and (write_only or neither):
                                writeSchema.properties.append(propertySchema)

                    if read and write:
                        return {
                                'Read': readSchema,
                                'Write': writeSchema
                                }
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
                    if issubclass(pkField, djangoFields.IntegerField) or pkField in [djangoFields.AutoField, djangoFields.BinaryField]:
                        schema.type = 'integer'
                    elif pkField in [djangoFields.BooleanField, djangoFields.NullBooleanField]:
                        schema.type = 'boolean'
                    elif pkField in [djangoFields.DecimalField, djangoFields.FloatField]:
                        schema.type = 'number'
                    elif issubclass(pkField, djangoFields.DateField) or pkField in [djangoFields.DurationField, djangoFields.TimeField]:
                        schema.type = 'date'
                    else:
                        schema.type = 'string'
                else:
                    schema.type = 'string'

                return schema

done = False
schemasDirectory = 'docs/schemas'

if os.path.exists(schemasDirectory):
    shutil.rmtree(schemasDirectory)

os.makedirs(schemasDirectory)


def lower(s):
    return s[:1].lower() + s[1:] if s else ''

schemaIncludeFile = open(schemasDirectory + '/include.raml', 'w+')

for folder, serializerModule in serializerModules.iteritems():
    directory = schemasDirectory + '/' + folder

    if not os.path.exists(directory):
        os.makedirs(directory)

    for name, obj in inspect.getmembers(serializerModule):
        if inspect.isclass(obj):
            if issubclass(obj, BaseSerializer):
                if not done:
                    schemas = Schema.getSchemas(obj())
                    if schemas is not None:
                        for permission, schema in schemas.iteritems():
                            data = json.dumps(schema, indent=4, cls=SchemaEncoder)

                            fileName = folder + name.replace('Serializer', '') + permission
                            relativeFilePath = '%s/%s.schema' % (folder, fileName)
                            absoluteFilePath = '%s/%s.schema' % (directory, fileName)

                            schemaFile = open(absoluteFilePath, 'w+')
                            schemaFile.write(data)
                            schemaFile.close()

                            schemaIncludeFile.write('- %s: !include %s\r\n' % (fileName, relativeFilePath,))

schemaIncludeFile.close()
