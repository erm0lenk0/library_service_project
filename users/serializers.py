from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    A basic serializer for displaying and editing users.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_staff",
        ]
        read_only_fields = ["id", "is_staff"]


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for registering/creating users.
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed user viewing.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
        ]
        read_only_fields = ["id", "is_staff", "is_superuser"]
