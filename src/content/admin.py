from django.contrib import admin

from content.models import EmailContent, AboutUs, FAQ


@admin.register(EmailContent)
class EmailContentAdmin(admin.ModelAdmin):
    list_display = ['language', 'purpose', 'subject', 'target', 'updated_at']


@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ['language', 'content']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['language', 'question', 'answer', 'order', 'active', 'updated_at']
