# Generated by Django 2.1.3 on 2018-12-06 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coin_exchange', '0012_review_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='SellingCODOrder',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('coin_exchange.order',),
        ),
        migrations.AddField(
            model_name='order',
            name='first_purchase',
            field=models.BooleanField(default=False),
        ),
    ]
