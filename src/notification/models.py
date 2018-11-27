from django.db import models

from coin_base.models import TimestampedModel
from notification.constants import NOTIFICATION_GROUP, NOTIFICATION_METHOD


class SystemReminder(models.Model):
    group = models.CharField(max_length=50, choices=NOTIFICATION_GROUP)
    method = models.CharField(max_length=50, choices=NOTIFICATION_METHOD)
    target = models.CharField(max_length=1000, blank=True)
    frequency = models.IntegerField(default=5)  # in minute
    times = models.IntegerField(default=1)
    break_duration = models.IntegerField(default=5)  # in minute
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return '%s by %s' % (self.group, self.method)


class SystemReminderAction(TimestampedModel):
    class Meta:
        unique_together = ('group', )

    group = models.CharField(max_length=50, choices=NOTIFICATION_GROUP)
    active_reminder = models.ForeignKey(SystemReminder, on_delete=models.CASCADE)
    active_time = models.IntegerField()
    stop_duration = models.IntegerField()


class SystemNotification(models.Model):
    class Meta:
        unique_together = ('group', 'method')

    group = models.CharField(max_length=50, choices=NOTIFICATION_GROUP)
    method = models.CharField(max_length=50, choices=NOTIFICATION_METHOD)
    target = models.CharField(max_length=1000, blank=True)
    active = models.BooleanField(default=True)
