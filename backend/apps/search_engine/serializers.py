from rest_framework import serializers
from .models import Destination


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ["id", "name", "country", "description", "avg_cost_per_day", "tags", "created_at"]
        read_only_fields = ["id", "created_at"]

class HotelSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    city = serializers.CharField()
    country = serializers.CharField()
    rating = serializers.FloatField()
    reviews = serializers.IntegerField()
    price_per_night = serializers.IntegerField()
    currency = serializers.CharField()
    description = serializers.CharField()
    amenities = serializers.ListField(child=serializers.CharField())
    tags = serializers.ListField(child=serializers.CharField())
    image_url = serializers.URLField()
    available = serializers.BooleanField()
