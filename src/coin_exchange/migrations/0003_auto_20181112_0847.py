# Generated by Django 2.1.3 on 2018-11-12 08:47

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('coin_user', '0002_auto_20181108_1746'),
        ('coin_exchange', '0002_auto_20181111_1619'),
    ]

    operations = [
        migrations.AddField(
            model_name='trackingaddress',
            name='status',
            field=models.CharField(choices=[('created', 'Created'), ('has_order', 'Has Order'), ('has_payment', 'Has Payment'), ('completed', 'Completed')], default='created', max_length=20),
        ),
        migrations.AddField(
            model_name='trackingaddress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user_addresses', to='coin_user.ExchangeUser'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='trackingaddress',
            unique_together={('user', 'address', 'currency')},
        ),
    ]