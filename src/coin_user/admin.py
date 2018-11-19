from django.contrib import admin

from coin_exchange.models import UserLimit
from coin_user.models import ExchangeUser


class UserLimitInline(admin.StackedInline):
    model = UserLimit
    fields = ('limit', 'usage')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ExchangeUser)
class ExchangeUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'id_number', 'id_type', 'front_image', 'back_image', 'selfie_image',
                    'verification_level', 'verification_status', 'country']
    inlines = (UserLimitInline,)
