# Generated by Django 2.2.6 on 2020-11-20 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0022_auto_20201120_0024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
