# Generated by Django 2.1.3 on 2018-11-15 06:43

import common.model_fields
from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AboutUs',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('language', common.model_fields.LanguageField(choices=[('km', 'Cambodian'), ('en', 'English'), ('id', 'Indonesian')], max_length=10, primary_key=True, serialize=False)),
                ('content', tinymce.models.HTMLField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EmailContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('purpose', models.CharField(choices=[('email_verification', 'Email verification')], max_length=100)),
                ('language', common.model_fields.LanguageField(choices=[('km', 'Cambodian'), ('en', 'English'), ('id', 'Indonesian')], max_length=10)),
                ('subject', models.CharField(max_length=500)),
                ('content', tinymce.models.HTMLField()),
                ('target', models.CharField(choices=[('user', 'User'), ('system', 'System')], max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('language', common.model_fields.LanguageField(choices=[('km', 'Cambodian'), ('en', 'English'), ('id', 'Indonesian')], max_length=10, primary_key=True, serialize=False)),
                ('question', models.CharField(max_length=500)),
                ('answer', tinymce.models.HTMLField()),
                ('order', models.IntegerField(default=1)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='emailcontent',
            unique_together={('purpose', 'language')},
        ),
    ]