from django.contrib import admin

from coin_system.models import Config, Fee, Bank, CountryCurrency, PopularPlace


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ['key', 'value']


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ['key', 'value']


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ['country', 'currency', 'bank_name']


@admin.register(CountryCurrency)
class CountryCurrencyAdmin(admin.ModelAdmin):
    list_display = ['country', 'currency', 'active']


@admin.register(PopularPlace)
class PopularPlaceAdmin(admin.ModelAdmin):
    list_display = ['country', 'name', 'address', 'active']
