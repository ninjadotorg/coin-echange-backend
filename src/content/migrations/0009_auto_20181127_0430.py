# Generated by Django 2.1.3 on 2018-11-27 04:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0008_auto_20181127_0345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staticpage',
            name='page',
            field=models.CharField(choices=[('about_us', 'About Us'), ('privacy', 'Privacy'), ('agreement', 'Agreement')], max_length=100),
        ),
    ]
