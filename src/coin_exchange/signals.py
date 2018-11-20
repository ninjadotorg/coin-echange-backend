from django.db.models.signals import post_save
from django.dispatch import receiver

from coin_exchange.business.user_limit import update_limit_by_level
from coin_user.constants import VERIFICATION_STATUS
from coin_user.models import ExchangeUser


@receiver(post_save, sender=ExchangeUser)
def post_exchange_user(sender, instance, created, **kwargs):
    update_fields = kwargs['update_fields']
    if not created and update_fields and 'verification_status' in update_fields:
        if instance.verification_status == VERIFICATION_STATUS.approved:
            update_limit_by_level(instance)
