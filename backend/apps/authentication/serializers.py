"""
Serializers for the authentication app.
"""

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """Validates login credentials (email OR username + password)."""

    # Accept either email or username in the same field for convenience.
    login = serializers.CharField(
        write_only=True,
        help_text="Email address or username.",
    )
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        login = attrs["login"].strip()
        password = attrs["password"]

        # Try email first, then username.
        user = None
        if "@" in login:
            try:
                db_user = User.objects.get(email__iexact=login)
                user = authenticate(username=db_user.username, password=password)
            except User.DoesNotExist:
                pass
        else:
            user = authenticate(username=login, password=password)

        if user is None:
            raise serializers.ValidationError(
                {"code": "invalid_credentials", "detail": "Invalid login or password."}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"code": "account_disabled", "detail": "This account is disabled."}
            )

        attrs["user"] = user
        return attrs


class UserMeSerializer(serializers.ModelSerializer):
    """Public representation of the currently authenticated user."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "bio", "avatar", "date_joined", "is_staff"]
        read_only_fields = fields
