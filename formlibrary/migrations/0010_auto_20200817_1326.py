# Generated by Django 2.2.13 on 2020-08-17 20:26

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0027_auto_20200428_0711'),
        ('formlibrary', '0009_merge_20200620_0127'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='create_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, null=True, verbose_name='Creation date'),
        ),
        migrations.AddField(
            model_name='case',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='workflow.ActivityUser', verbose_name='Created by'),
        ),
        migrations.AddField(
            model_name='case',
            name='modified_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='workflow.ActivityUser', verbose_name='Last Modified by'),
        ),
        migrations.AddField(
            model_name='case',
            name='modified_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Last Modification date'),
        ),
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
