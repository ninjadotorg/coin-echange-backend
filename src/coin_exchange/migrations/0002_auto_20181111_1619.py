# Generated by Django 2.1.3 on 2018-11-11 16:19

import common.model_fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coin_exchange', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='center',
        ),
        migrations.AlterField(
            model_name='order',
            name='receipt_url',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='tx_hash',
            field=common.model_fields.CryptoHashField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='review',
            unique_together=set(),
        ),
    ]
