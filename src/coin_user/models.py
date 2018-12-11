from django.contrib.auth.models import User
from django.db import models

from coin_base.models import TimestampedModel
from coin_user.constants import VERIFICATION_LEVEL, ID_TYPE, VERIFICATION_STATUS, PAYMENT_VERIFICATION_STATUS
from common.constants import LANGUAGE, COUNTRY, FIAT_CURRENCY


class ExchangeUser(models.Model):
    class Meta:
        verbose_name = 'Exch User'
        verbose_name_plural = 'Exch Users'

    user = models.OneToOneField(User, related_name='exchange_user', on_delete=models.CASCADE)
    user = models.OneToOneField(User, related_name='exchange_user', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    pending_phone_number = models.CharField(max_length=20, blank=True)
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
    phone_retry = models.IntegerField(default=10)
    security_2fa = models.BooleanField(default=False)
    security_2fa_secret = models.CharField(max_length=500, null=True, blank=True)
    language = models.CharField(max_length=10, choices=LANGUAGE, null=True)
    country = models.CharField(max_length=3, choices=COUNTRY, null=True)
    currency = models.CharField(max_length=5, choices=FIAT_CURRENCY, null=True)
    wallet = models.TextField(null=True, blank=True)
    payment_info = models.TextField(null=True, blank=True)
    payment_verification_status = models.CharField(max_length=30, choices=PAYMENT_VERIFICATION_STATUS,
                                                   default=PAYMENT_VERIFICATION_STATUS.not_yet)
    referral = models.ForeignKey('ExchangeUser', null=True, blank=True, related_name='referral_users',
                                 on_delete=models.SET_NULL)
    first_purchase = models.DateTimeField(null=True)

    def __str__(self):
        return '%s' % self.user.username

    def approve_verification(self):
        self._change_verification_status(VERIFICATION_STATUS.approved)

    def reject_verification(self):
        self._change_verification_status(VERIFICATION_STATUS.rejected)

    def process_verification(self):
        self._change_verification_status(VERIFICATION_STATUS.processing)

    def _change_verification_status(self, status):
        self.verification_status = status
        self.save(update_fields=['phone_number', 'pending_phone_number', 'verification_status'])

    def change_payment_verification(self, save=True):
        self._change_payment_verification_status(PAYMENT_VERIFICATION_STATUS.pending, save=save)

    def approve_payment_verification(self):
        self._change_payment_verification_status(PAYMENT_VERIFICATION_STATUS.verified, save=True)

    def reject_payment_verification(self):
        self._change_payment_verification_status(PAYMENT_VERIFICATION_STATUS.rejected, save=True)

    def process_payment_verification(self):
        self._change_payment_verification_status(PAYMENT_VERIFICATION_STATUS.processing, save=True)

    def _change_payment_verification_status(self, status, save=True):
        self.payment_verification_status = status
        if save:
            self.save(update_fields=['payment_info', 'payment_verification_status'])


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
