# Generated by Django 2.2.6 on 2020-11-17 22:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0014_pointofinterest_species'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PointOfInterest',
            new_name='Location',
        ),
    ]
