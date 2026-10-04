from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.serializers import Serializer

from apps.auths.serializers import UserRegistrationSerializer


class UserRegistrationView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def get_serializer_class(self) -> type[Serializer]:
        return self.serializer_class
