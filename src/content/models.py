from django.db import models
from tinymce.models import HTMLField

from coin_base.models import TimestampedModel
from coin_system.constants import EMAIL_PURPOSE, EMAIL_TARGET
from common import model_fields


class EmailContent(TimestampedModel):
    class Meta:
        unique_together = ('purpose', 'language')

    purpose = models.CharField(max_length=100, choices=EMAIL_PURPOSE)
    language = model_fields.LanguageField()
    subject = models.CharField(max_length=500)
    content = HTMLField()
    target = models.CharField(max_length=100, choices=EMAIL_TARGET)


class AboutUs(TimestampedModel):
    language = model_fields.LanguageField(primary_key=True)
    content = HTMLField()


class FAQ(TimestampedModel):
    language = model_fields.LanguageField()
    question = models.CharField(max_length=500)
    answer = HTMLField()
    order = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
