from rest_framework import serializers

from content.models import FAQ, StaticPage


class StaticPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = '__all__'

    title = serializers.CharField(source='get_title', read_only=True)


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'
