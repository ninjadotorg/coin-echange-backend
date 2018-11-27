from django.contrib import admin

from notification.models import SystemReminder, SystemReminderAction, SystemNotification


@admin.register(SystemReminder)
class SystemReminderAdmin(admin.ModelAdmin):
    list_display = ['group', 'method', 'target', 'frequency', 'times', 'break_duration', 'order', 'active']


@admin.register(SystemReminderAction)
class SystemReminderActionAdmin(admin.ModelAdmin):
    list_display = ['group', 'active_reminder', 'active_time', 'stop_duration']


@admin.register(SystemNotification)
class SystemNotificationAdmin(admin.ModelAdmin):
    list_display = ['group', 'method', 'active']
