from django.contrib.auth.models import User
from django.db import models

from coin_base.models import TimestampedModel
from coin_user.constants import VERIFICATION_LEVEL, ID_TYPE, VERIFICATION_STATUS
from common.constants import LANGUAGE, COUNTRY, FIAT_CURRENCY


class ExchangeUser(models.Model):
    user = models.OneToOneField(User, related_name='exchange_user', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    id_name = models.CharField(max_length=100, blank=True)
    id_number = models.CharField(max_length=100, blank=True)
    id_type = models.CharField(max_length=30, choices=ID_TYPE, null=True)
    front_image = models.CharField(max_length=500, blank=True)
    back_image = models.CharField(max_length=500, blank=True)
    selfie_image = models.CharField(max_length=500, blank=True)
    verification_level = models.CharField(max_length=30, choices=VERIFICATION_LEVEL, default=VERIFICATION_LEVEL.level_0)
    verification_status = models.CharField(max_length=30, choices=VERIFICATION_STATUS,
                                           default=VERIFICATION_STATUS.not_yet)
    email_verification_code = models.CharField(max_length=20, blank=True)
    phone_verification_code = models.CharField(max_length=10, blank=True)
    language = models.CharField(max_length=10, choices=LANGUAGE, null=True)
    country = models.CharField(max_length=3, choices=COUNTRY, null=True)
    currency = models.CharField(max_length=5, choices=FIAT_CURRENCY, null=True)
    wallet = models.TextField(null=True, blank=True)

    def __str__(self):
        return '%s' % self.user.username

    def approve_verification(self):
        self._change_verificaiton_status(VERIFICATION_STATUS.approved)

    def reject_verification(self):
        self._change_verificaiton_status(VERIFICATION_STATUS.rejected)

    def process_verification(self):
        self._change_verificaiton_status(VERIFICATION_STATUS.processing)

    def _change_verificaiton_status(self, status):
        self.verification_status = status
        self.save(update_fields=['verification_status'])


class AdminUser(models.Model):
    user = models.OneToOneField(User, related_name='admin_user', on_delete=models.CASCADE)

    def __str__(self):
        return '%s' % self.user.username


class Contact(TimestampedModel):
    user = models.ForeignKey(ExchangeUser, related_name='user_contacts', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    description = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return '%s' % self.name
