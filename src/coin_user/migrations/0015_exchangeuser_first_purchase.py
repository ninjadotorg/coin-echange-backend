# Generated by Django 2.1.3 on 2018-11-28 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coin_user', '0014_exchangeuser_phone_retry'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchangeuser',
            name='first_purchase',
            field=models.BooleanField(default=False),
        ),
    ]
