# Generated by Django 2.1.3 on 2018-11-16 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coin_user', '0002_auto_20181116_0840'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchangeuser',
            name='wallet',
            field=models.TextField(blank=True, null=True),
        ),
    ]
