# Generated by Django 2.2.6 on 2020-11-16 23:28

from django.db import migrations
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0011_auto_20201115_2030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=versatileimagefield.fields.VersatileImageField(blank=True, height_field='height', null=True, upload_to='images/', verbose_name='Image', width_field='width'),
        ),
    ]
