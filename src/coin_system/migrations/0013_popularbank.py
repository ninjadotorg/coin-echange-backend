# Generated by Django 2.1.3 on 2018-12-04 14:30

import common.model_fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coin_system', '0012_popularplace_language'),
    ]

    operations = [
        migrations.CreateModel(
            name='PopularBank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', common.model_fields.CountryField(choices=[('KH', 'Cambodia'), ('ID', 'Indonesia'), ('PH', 'Philippines'), ('HK', 'Hong Kong')], max_length=3)),
                ('language', common.model_fields.LanguageField(blank=True, choices=[('km', '🇰🇭 ភាសាខ្មែរ'), ('en', '🇺🇸 English'), ('id', '🇮🇩 bahasa Indonesia'), ('zh-Hant-HK', '🇭🇰 廣東話')], max_length=10, null=True)),
                ('name', models.CharField(max_length=100)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
    ]
