from rest_framework import serializers
from .models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            "id",
            "jam",
            "description",
            "amount",
            "category",
            "paid_by",
            "split_between",
            "date",
            "created_at",
        ]
        read_only_fields = ["id", "paid_by", "date", "created_at"]
