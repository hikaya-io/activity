# Generated by Django 2.2.10 on 2020-03-10 17:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indicators', '0009_merge_20200228_0054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='level',
            name='create_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, null=True),
        ),
    ]
