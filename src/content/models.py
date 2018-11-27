from django.db import models
from tinymce.models import HTMLField

from coin_base.models import TimestampedModel
from coin_system.constants import EMAIL_PURPOSE, NOTIFICATION_TARGET, SMS_PURPOSE, STATIC_PAGE
from common import model_fields


class EmailContent(TimestampedModel):
    class Meta:
        unique_together = ('purpose', 'language')

    purpose = models.CharField(max_length=100, choices=EMAIL_PURPOSE)
    language = model_fields.LanguageField()
    subject = models.CharField(max_length=500)
    content = HTMLField()
    target = models.CharField(max_length=100, choices=NOTIFICATION_TARGET)


class SMSContent(TimestampedModel):
    class Meta:
        unique_together = ('purpose', 'language')

    purpose = models.CharField(max_length=100, choices=SMS_PURPOSE)
    language = model_fields.LanguageField()
    content = models.CharField(max_length=200)
    target = models.CharField(max_length=100, choices=NOTIFICATION_TARGET)


# DEPRECATED
class AboutUs(TimestampedModel):
    language = model_fields.LanguageField(primary_key=True)
    content = HTMLField()


class StaticPage(TimestampedModel):
    class Meta:
        unique_together = ('page', 'language')

    page = models.CharField(max_length=100, choices=STATIC_PAGE)
    language = model_fields.LanguageField()
    content = HTMLField()


class FAQ(TimestampedModel):
    language = model_fields.LanguageField()
    question = models.CharField(max_length=500)
    answer = HTMLField()
    order = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
