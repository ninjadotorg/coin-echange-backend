from django.contrib import admin

from coin_user.models import ExchangeUser


@admin.register(ExchangeUser)
class ExchangeUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'id_number', 'id_type', 'front_image', 'back_image', 'selfie_image',
                    'verification_level', 'verification_status', 'country']
