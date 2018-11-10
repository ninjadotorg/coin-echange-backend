from rest_framework import serializers

from coin_exchange.models import Order
from common import serializer_fields


class QuoteInputSerializer(serializers.Serializer):
    amount = serializer_fields.CryptoAmountField()
    currency = serializer_fields.CryptoCurrencyField()
    fiat_currency = serializer_fields.FiatCurrencyField()
    pool_check = serializers.BooleanField()
    user_check = serializers.BooleanField()


class QuoteSerializer(serializers.Serializer):
    fiat_amount = serializer_fields.FiatAmountField()
    fiat_currency = serializer_fields.FiatCurrencyField()
    fiat_local_amount = serializer_fields.FiatAmountField()
    fiat_local_currency = serializer_fields.FiatCurrencyField()
    fiat_amount_cod = serializer_fields.FiatAmountField()
    fiat_local_amount_cod = serializer_fields.FiatAmountField()
    fee = serializer_fields.FiatAmountField()
    fee_cod = serializer_fields.FiatAmountField()
    fee_local = serializer_fields.FiatAmountField()
    fee_local_cod = serializer_fields.FiatAmountField()
    price = serializer_fields.FiatAmountField()
    amount = serializer_fields.CryptoAmountField()
    currency = serializer_fields.CryptoCurrencyField()


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
