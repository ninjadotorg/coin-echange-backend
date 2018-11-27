from django.contrib import admin

from content.models import EmailContent, FAQ, SMSContent, StaticPage


@admin.register(EmailContent)
class EmailContentAdmin(admin.ModelAdmin):
    list_display = ['purpose', 'language', 'subject', 'target', 'updated_at']
    list_filter = ('language', 'purpose', )


@admin.register(SMSContent)
class SMSContentAdmin(admin.ModelAdmin):
    list_display = ['purpose', 'language', 'content', 'target', 'updated_at']
    list_filter = ('purpose',)


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ['page', 'language']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'language', 'order', 'active', 'updated_at']
    list_filter = ('language', )
