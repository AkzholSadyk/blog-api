from django.urls import path

from apps.auths.views import UserRegistrationView


REGISTER_URL = "register/"


urlpatterns = [
    path(
        REGISTER_URL,
        UserRegistrationView.as_view(),
        name="register",
    ),
]
