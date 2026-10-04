from rest_framework import serializers

from apps.auths.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "password",
        )

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password")

        return User.objects.create_user(
            password=password,
            **validated_data,
        )
