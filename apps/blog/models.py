from django.conf import settings
from django.db import models


CATEGORY_NAME_MAX_LENGTH = 100
CATEGORY_SLUG_MAX_LENGTH = 100
TAG_NAME_MAX_LENGTH = 50
TAG_SLUG_MAX_LENGTH = 50
POST_TITLE_MAX_LENGTH = 200
POST_SLUG_MAX_LENGTH = 200

DRAFT_STATUS = "draft"
PUBLISHED_STATUS = "published"


class Category(models.Model):
    name = models.CharField(
        max_length=CATEGORY_NAME_MAX_LENGTH,
        unique=True,
    )
    slug = models.SlugField(
        max_length=CATEGORY_SLUG_MAX_LENGTH,
        unique=True,
    )

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=TAG_NAME_MAX_LENGTH,
        unique=True,
    )
    slug = models.SlugField(
        max_length=TAG_SLUG_MAX_LENGTH,
        unique=True,
    )

    def __str__(self) -> str:
        return self.name


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = DRAFT_STATUS, "Draft"
        PUBLISHED = PUBLISHED_STATUS, "Published"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    title = models.CharField(max_length=POST_TITLE_MAX_LENGTH)
    slug = models.SlugField(
        max_length=POST_SLUG_MAX_LENGTH,
        unique=True,
    )
    body = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="posts",
    )
    status = models.CharField(
        max_length=max(
            len(DRAFT_STATUS),
            len(PUBLISHED_STATUS),
        ),
        choices=Status.choices,
        default=Status.DRAFT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Comment #{self.pk}"
