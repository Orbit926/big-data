from rest_framework import serializers
from .models import Destination


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ["id", "name", "country", "description", "avg_cost_per_day", "tags", "created_at"]
        read_only_fields = ["id", "created_at"]
