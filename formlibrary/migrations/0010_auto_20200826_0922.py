# Generated by Django 2.2.13 on 2020-08-26 16:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formlibrary', '0009_merge_20200620_0127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='construction',
            name='create_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, null=True, verbose_name='Creation date'),
        ),
        migrations.AlterField(
            model_name='distribution',
            name='create_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, null=True, verbose_name='Creation date'),
        ),
        migrations.AlterField(
            model_name='individual',
            name='create_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, null=True, verbose_name='Creation date'),
        ),
        migrations.AlterField(
            model_name='training',
            name='create_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, null=True, verbose_name='Creation date'),
        ),
    ]
