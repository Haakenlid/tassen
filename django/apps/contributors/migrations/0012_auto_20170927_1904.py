# Generated by Django 1.11 on 2017-09-27 17:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contributors', '0011_auto_20170927_1506'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contributor',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
