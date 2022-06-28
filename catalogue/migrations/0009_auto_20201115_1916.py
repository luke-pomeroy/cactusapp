# Generated by Django 2.2.6 on 2020-11-15 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0008_remove_photo_ppoi'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='species',
            name='phylum',
        ),
        migrations.AddField(
            model_name='species',
            name='author',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='species',
            name='source',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='species',
            name='url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='speciesdescription',
            name='order',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
