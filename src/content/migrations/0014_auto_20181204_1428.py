# Generated by Django 2.1.3 on 2018-12-04 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0013_auto_20181202_0509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staticpage',
            name='page',
            field=models.CharField(choices=[('about_us', 'About Us'), ('privacy', 'Privacy'), ('agreement', 'Agreement'), ('promotion_programs', 'Promotion Programs'), ('how_it_works', 'How It Works')], max_length=100),
        ),
    ]