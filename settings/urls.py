from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


ADMIN_URL = "admin/"
AUTH_URL = "api/auth/"
AUTH_TOKEN_URL = "token/"
AUTH_TOKEN_REFRESH_URL = "token/refresh/"
BLOG_URL = "api/blog/"


urlpatterns = [
    path(ADMIN_URL, admin.site.urls),
    path(AUTH_URL, include("apps.auths.urls")),
    path(
        f"{AUTH_URL}{AUTH_TOKEN_URL}",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        f"{AUTH_URL}{AUTH_TOKEN_REFRESH_URL}",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(BLOG_URL, include("apps.blog.urls")),
]
