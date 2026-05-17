"""
Serializers for the authentication app.

LoginSerializer    — validates login credentials (email OR username + password)
RegisterSerializer — validates and creates a new user account
UserMeSerializer   — read-only representation of the authenticated user's session profile

Note: UserMeSerializer intentionally lives here (not in apps.users) because it is
exclusively used by the /me/ session endpoint and must stay in sync with the JWT
payload fields. The richer profile serializer lives in apps.users.serializers.
"""

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


# ── Login ──────────────────────────────────────────────────────────────────────


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


# ── Register ───────────────────────────────────────────────────────────────────


class RegisterSerializer(serializers.Serializer):
    """
    Validates registration data and creates a new User.

    Uses get_user_model() so this serializer works with any custom user model
    (currently apps.users.User).  Password validation runs Django's built-in
    AUTH_PASSWORD_VALIDATORS.
    """

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text="Must match the password field.",
    )
    # Optional profile fields
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    # ── Field-level validations ────────────────────────────────────────────────

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value.lower()

    # ── Cross-field validations ────────────────────────────────────────────────

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        # Run Django's password validators (length, common passwords, etc.)
        validate_password(attrs["password"])
        return attrs

    # ── Creation ───────────────────────────────────────────────────────────────

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# ── Session profile (used by /me/) ────────────────────────────────────────────


class UserMeSerializer(serializers.ModelSerializer):
    """
    Read-only profile of the currently authenticated user.
    Used exclusively by MeView — mirrors the JWT payload fields plus
    a few extras useful for the frontend session context.
    """

    class Meta:
        model = User
        fields = ["id", "username", "email", "bio", "avatar", "date_joined", "is_staff"]
        read_only_fields = fields
