# Generated by Django 2.1.3 on 2018-11-28 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coin_user', '0013_exchangeuser_pending_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchangeuser',
            name='phone_retry',
            field=models.IntegerField(default=10),
        ),
    ]