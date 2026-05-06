from rest_framework import serializers
from .models import Jam


class JamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jam
        fields = ["id", "trip", "name", "members", "created_by", "created_at"]
        read_only_fields = ["id", "created_by", "created_at"]
