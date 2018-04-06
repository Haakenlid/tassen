# Generated by Django 1.11 on 2017-10-16 20:30

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0028_auto_20170928_2041'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
        migrations.AddIndex(
            model_name='story',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_vector'], name='stories_sto_search__18a3ad_gin'),
        ),
    ]
