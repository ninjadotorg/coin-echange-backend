from rest_framework import serializers


class PriceSerialize(serializers.Serializer):
    fiat_amount = serializers.DecimalField(max_digits=20, decimal_places=4)
    fiat_currency = serializers.CharField()
    fiat_local_amount = serializers.DecimalField(max_digits=20, decimal_places=4)
    fiat_local_currency = serializers.CharField()
    fiat_amount_cod = serializers.DecimalField(max_digits=20, decimal_places=4)
    fiat_local_amount_cod = serializers.DecimalField(max_digits=20, decimal_places=4)
    price = serializers.DecimalField(max_digits=20, decimal_places=4)
