import json

from django.conf import settings
from django.db.models import Count
from django.http import HttpRequest
from django.urls import reverse

from apps.auths.models import User
from apps.blog.models import Category, Comment, Post

TOP_AUTHORS_LIMIT = 5


def environment_callback(request: HttpRequest) -> list[str]:
    if settings.BLOG_ENV_ID == "production":
        return ["Production", "danger"]
    return ["Local", "warning"]


def drafts_badge_callback(request: HttpRequest) -> int:
    return Post.objects.filter(status=Post.Status.DRAFT).count()


def users_section_visible(request: HttpRequest) -> bool:
    return request.user.is_superuser


def all_posts_link(request: HttpRequest) -> str:
    return reverse("admin:blog_post_changelist")


def published_posts_link(request: HttpRequest) -> str:
    return f"{reverse('admin:blog_post_changelist')}?status__exact=published"


def draft_posts_link(request: HttpRequest) -> str:
    return f"{reverse('admin:blog_post_changelist')}?status__exact=draft"


def dashboard_callback(request: HttpRequest, context: dict) -> dict:
    published_count = Post.objects.filter(status=Post.Status.PUBLISHED).count()
    draft_count = Post.objects.filter(status=Post.Status.DRAFT).count()
    total_posts = published_count + draft_count

    category_rows = list(
        Category.objects.annotate(posts_count=Count("posts"))
        .order_by("-posts_count")
        .values_list("name", "posts_count"),
    )
    top_authors = User.objects.annotate(posts_count=Count("posts")).order_by(
        "-posts_count",
    )[:TOP_AUTHORS_LIMIT]

    posts_per_category_chart = {
        "labels": [name for name, _count in category_rows],
        "datasets": [
            {
                "label": "Posts",
                "data": [count for _name, count in category_rows],
            },
        ],
    }

    context.update(
        {
            "cards": [
                {"title": "Users", "metric": User.objects.count()},
                {"title": "Published posts", "metric": published_count},
                {"title": "Drafts", "metric": draft_count},
                {"title": "Comments", "metric": Comment.objects.count()},
            ],
            "posts_per_category_chart": json.dumps(posts_per_category_chart),
            "top_authors_table": {
                "headers": ["Author", "Posts"],
                "rows": [
                    [f"{author.first_name} {author.last_name}", author.posts_count]
                    for author in top_authors
                ],
            },
            "published_share": (
                round(published_count / total_posts * 100) if total_posts else 0
            ),
            "draft_share": (
                round(draft_count / total_posts * 100) if total_posts else 0
            ),
        },
    )
    return context