from pathlib import Path

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from settings.conf import (
    BLOG_ALLOWED_HOSTS,
    BLOG_DEBUG,
    BLOG_ENV_ID,
    BLOG_SECRET_KEY,
)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = BLOG_SECRET_KEY

DEBUG = BLOG_DEBUG

ALLOWED_HOSTS = BLOG_ALLOWED_HOSTS

BLOG_ENV_ID = BLOG_ENV_ID  # noqa: PLW0127 -- re-exported as a Django setting


INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.auths",
    "apps.blog",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "settings.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "settings.wsgi.application"

ASGI_APPLICATION = "settings.asgi.application"


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": ("django.contrib.auth.password_validation.MinimumLengthValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation.CommonPasswordValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation.NumericPasswordValidator"),
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Almaty"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


AUTH_USER_MODEL = "auths.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}


UNFOLD = {
    "SITE_TITLE": "Blog API",
    "SITE_HEADER": "Blog API",
    "SITE_SUBHEADER": "Content administration",
    "SITE_SYMBOL": "rss_feed",
    "ENVIRONMENT": "apps.blog.callbacks.environment_callback",
    "DASHBOARD_CALLBACK": "apps.blog.callbacks.dashboard_callback",
    "COLORS": {
        "primary": {
            "50": "239 246 255",
            "100": "219 234 254",
            "200": "191 219 254",
            "300": "147 197 253",
            "400": "96 165 250",
            "500": "59 130 246",
            "600": "37 99 235",
            "700": "29 78 216",
            "800": "30 64 175",
            "900": "30 58 138",
            "950": "23 37 84",
        },
    },
    "SITE_DROPDOWN": [
        {
            "icon": "code",
            "title": _("GitHub repository"),
            "link": "https://github.com/AkzholSadyk/blog-api",
        },
        {
            "icon": "menu_book",
            "title": _("Unfold docs"),
            "link": "https://unfoldadmin.com/docs/",
        },
    ],
    "COMMAND": {
        "search_models": True,
    },
    "SIDEBAR": {
        "show_search": True,
        "navigation": [
            {
                "title": _("Overview"),
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": _("Content"),
                "items": [
                    {
                        "title": _("Posts"),
                        "icon": "article",
                        "link": reverse_lazy("admin:blog_post_changelist"),
                        "badge": "apps.blog.callbacks.drafts_badge_callback",
                    },
                    {
                        "title": _("Comments"),
                        "icon": "comment",
                        "link": reverse_lazy("admin:blog_comment_changelist"),
                    },
                    {
                        "title": _("Categories"),
                        "icon": "category",
                        "link": reverse_lazy("admin:blog_category_changelist"),
                    },
                    {
                        "title": _("Tags"),
                        "icon": "sell",
                        "link": reverse_lazy("admin:blog_tag_changelist"),
                    },
                ],
            },
            {
                "title": _("Users & Access"),
                "permission": "apps.blog.callbacks.users_section_visible",
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "group",
                        "link": reverse_lazy("admin:auths_user_changelist"),
                    },
                    {
                        "title": _("Groups"),
                        "icon": "shield",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },
    "TABS": [
        {
            "models": ["blog.post"],
            "items": [
                {"title": _("All"), "link": "apps.blog.callbacks.all_posts_link"},
                {
                    "title": _("Published"),
                    "link": "apps.blog.callbacks.published_posts_link",
                },
                {
                    "title": _("Drafts"),
                    "link": "apps.blog.callbacks.draft_posts_link",
                },
            ],
        },
    ],
}
