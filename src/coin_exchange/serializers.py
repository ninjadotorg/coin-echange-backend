from rest_framework import serializers

from coin_exchange.models import Order, Review, ReferralOrder, PromotionOrder
from common import serializer_fields


class QuoteInputSerializer(serializers.Serializer):
    amount = serializer_fields.CryptoAmountField()
    currency = serializer_fields.CryptoCurrencyField()
    fiat_currency = serializer_fields.FiatCurrencyField()
    pool_check = serializers.BooleanField()
    user_check = serializers.BooleanField()
    direction = serializer_fields.DirectionField()


class QuoteSerializer(serializers.Serializer):
    fiat_amount = serializer_fields.FiatAmountField()
    fiat_currency = serializer_fields.FiatCurrencyField()
    fiat_local_amount = serializer_fields.FiatAmountField()
    fiat_local_currency = serializer_fields.FiatCurrencyField()
    fiat_amount_cod = serializer_fields.FiatAmountField()
    fiat_local_amount_cod = serializer_fields.FiatAmountField()
    raw_fiat_amount = serializer_fields.FiatAmountField()
    fee = serializer_fields.FiatAmountField()
    fee_cod = serializer_fields.FiatAmountField()
    fee_local = serializer_fields.FiatAmountField()
    fee_local_cod = serializer_fields.FiatAmountField()
    price = serializer_fields.FiatAmountField()
    amount = serializer_fields.CryptoAmountField()
    currency = serializer_fields.CryptoCurrencyField()
    direction = serializer_fields.DirectionField()


class QuoteReverseInputSerializer(serializers.Serializer):
    currency = serializer_fields.CryptoCurrencyField()
    fiat_amount = serializer_fields.CryptoAmountField()
    fiat_currency = serializer_fields.FiatCurrencyField()
    pool_check = serializers.BooleanField()
    user_check = serializers.BooleanField()
    direction = serializer_fields.DirectionField()
    order_type = serializers.CharField()


class QuoteReverseSerializer(serializers.Serializer):
    fiat_amount = serializer_fields.FiatAmountField()
    fiat_currency = serializer_fields.FiatCurrencyField()
    fiat_local_amount = serializer_fields.FiatAmountField()
    fiat_local_currency = serializer_fields.FiatCurrencyField()
    raw_fiat_amount = serializer_fields.FiatAmountField()
    price = serializer_fields.FiatAmountField()
    amount = serializer_fields.CryptoAmountField()
    currency = serializer_fields.CryptoCurrencyField()
    direction = serializer_fields.DirectionField()


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ('user', 'raw_fiat_amount', 'price', 'fee', 'provider_data')
        read_only_fields = ('fiat_amount', 'fiat_currency', 'ref_code', 'reviewed')


class SellingOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ('user', 'raw_fiat_amount', 'price', 'fee', 'receipt_url', 'provider_data')
        read_only_fields = ('fiat_amount', 'fiat_currency', 'ref_code', 'reviewed')


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('name', 'review', 'order')
        extra_kwargs = {'order': {'write_only': True}}


class ReferralOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralOrder
        fields = '__all__'


class PromotionOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionOrder
        fields = '__all__'
