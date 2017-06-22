from __future__ import unicode_literals

from django.conf import settings
from django.db import connection, migrations, models


def migrate_model(model, db_source, db_dest):
    if model._meta.db_table not in connection.introspection.table_names():
        print(
            'Not migrating model {model} because its table does not exist.'.format(
                model=model
            )
        )
        return
    print('model', model)
    # remove data from destination db before copying
    # to avoid primary key conflicts or mismatches
    if model.objects.using(db_dest).exists():
        model.objects.using(db_dest).all().delete()

    # get data form the source database
    items = model.objects.using(db_source).all()

    # process in chunks, to handle models with lots of data
    for i in range(0, len(items), 1000):
        chunk_items = items[i:i + 1000]
        model.objects.using(db_dest).bulk_create(chunk_items)

    # many-to-many fields are NOT handled by bulk create; check for
    # them and use the existing implicit through models to copy them
    for m2mfield in model._meta.many_to_many:
        m2m_model = getattr(model, m2mfield.name).through
        migrate_model(
            model=m2m_model,
            db_source=db_source,
            db_dest=db_dest
        )


def postgres_migration_forward(apps, schema_editor):
    all_models = apps.get_models()

    for model in all_models:
        migrate_model(
            model=model,
            db_source='mysql',
            db_dest='default'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(postgres_migration_forward)
    ]
