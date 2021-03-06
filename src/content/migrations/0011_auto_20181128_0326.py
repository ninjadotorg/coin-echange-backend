# Generated by Django 2.1.3 on 2018-11-28 03:26

import common.model_fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0010_delete_aboutus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailcontent',
            name='language',
            field=common.model_fields.LanguageField(choices=[('km', '🇰🇭 ភាសាខ្មែរ'), ('en', '🇺🇸 English'), ('id', '🇮🇩 bahasa Indonesia'), ('hk', '🇭🇰 廣東話')], max_length=10),
        ),
        migrations.AlterField(
            model_name='faq',
            name='language',
            field=common.model_fields.LanguageField(choices=[('km', '🇰🇭 ភាសាខ្មែរ'), ('en', '🇺🇸 English'), ('id', '🇮🇩 bahasa Indonesia'), ('hk', '🇭🇰 廣東話')], max_length=10),
        ),
        migrations.AlterField(
            model_name='smscontent',
            name='language',
            field=common.model_fields.LanguageField(choices=[('km', '🇰🇭 ភាសាខ្មែរ'), ('en', '🇺🇸 English'), ('id', '🇮🇩 bahasa Indonesia'), ('hk', '🇭🇰 廣東話')], max_length=10),
        ),
        migrations.AlterField(
            model_name='staticpage',
            name='language',
            field=common.model_fields.LanguageField(choices=[('km', '🇰🇭 ភាសាខ្មែរ'), ('en', '🇺🇸 English'), ('id', '🇮🇩 bahasa Indonesia'), ('hk', '🇭🇰 廣東話')], max_length=10),
        ),
    ]
