from django.contrib.auth.models import User
from django.db import models

from coin_base.constants import VERIFICATION_LEVEL


class ExchangeUser(models.Model):
    user = models.OneToOneField(User, related_name='exchange_user', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)
    verification_level = models.CharField(max_length=30, choices=VERIFICATION_LEVEL, default=VERIFICATION_LEVEL.level_1)

    def __str__(self):
        return '%s' % self.user.username


class AdminUser(models.Model):
    user = models.OneToOneField(User, related_name='admin_user', on_delete=models.CASCADE)

    def __str__(self):
        return '%s' % self.user.username
