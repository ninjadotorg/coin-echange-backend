# Generated by Django 2.1.3 on 2018-12-10 08:44

import common.model_fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coin_exchange', '0014_auto_20181210_0754'),
    ]

    operations = [
        migrations.AddField(
            model_name='promotionuser',
            name='referral_amount',
            field=common.model_fields.FiatAmountField(decimal_places=2, default=0, max_digits=18),
        ),
    ]
