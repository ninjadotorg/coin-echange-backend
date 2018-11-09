from rest_framework import serializers

from coin_system.models import Bank, PopularPlace, CountryCurrency


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = '__all__'


class CountryCurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryCurrency
        fields = ('currency', )


class PopularPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PopularPlace
        fields = '__all__'
