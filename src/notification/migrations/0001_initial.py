# Generated by Django 2.1.3 on 2018-11-29 04:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SystemNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.CharField(choices=[('verification', 'Verification'), ('order', 'Order')], max_length=50)),
                ('method', models.CharField(choices=[('email', 'Email'), ('slack', 'Slack'), ('sms', 'SMS'), ('call', 'Call')], max_length=50)),
                ('target', models.CharField(blank=True, max_length=1000)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='SystemReminder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.CharField(choices=[('verification', 'Verification'), ('order', 'Order')], max_length=50)),
                ('method', models.CharField(choices=[('email', 'Email'), ('slack', 'Slack'), ('sms', 'SMS'), ('call', 'Call')], max_length=50)),
                ('target', models.CharField(blank=True, max_length=1000)),
                ('frequency', models.IntegerField(default=5)),
                ('times', models.IntegerField(default=1)),
                ('break_duration', models.IntegerField(default=5)),
                ('order', models.IntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='SystemReminderAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('group', models.CharField(choices=[('verification', 'Verification'), ('order', 'Order')], max_length=50)),
                ('active_time', models.IntegerField()),
                ('stop_duration', models.IntegerField()),
                ('active_reminder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notification.SystemReminder')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='systemnotification',
            unique_together={('group', 'method')},
        ),
        migrations.AlterUniqueTogether(
            name='systemreminderaction',
            unique_together={('group',)},
        ),
    ]
