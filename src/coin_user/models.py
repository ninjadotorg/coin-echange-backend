from django.contrib.auth.models import User
from django.db import models

from coin_user.constants import VERIFICATION_LEVEL, ID_TYPE, VERIFICATION_STATUS


class ExchangeUser(models.Model):
    user = models.OneToOneField(User, related_name='exchange_user', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)
    verification_level = models.CharField(max_length=30, choices=VERIFICATION_LEVEL, default=VERIFICATION_LEVEL.level_0)
    id_number = models.CharField(max_length=100, blank=True)
    id_type = models.CharField(max_length=30, choices=ID_TYPE, null=True)
    front_image = models.CharField(max_length=500, blank=True)
    back_image = models.CharField(max_length=500, blank=True)
    selfie_image = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=30, choices=VERIFICATION_STATUS, null=True)
    language = models.CharField(max_length=10, null=True)

    def __str__(self):
        return '%s' % self.user.username


class AdminUser(models.Model):
    user = models.OneToOneField(User, related_name='admin_user', on_delete=models.CASCADE)

    def __str__(self):
        return '%s' % self.user.username
