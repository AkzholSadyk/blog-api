from django.contrib import admin, messages
from django.contrib.auth.models import Group
from django.db import models
from django.db.models import Count, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    AutocompleteSelectFilter,
    ChoicesDropdownFilter,
    MultipleRelatedDropdownFilter,
    RangeDateTimeFilter,
    RelatedDropdownFilter,
)
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.decorators import action, display

from apps.blog.models import Category, Comment, Post, Tag

COMMENT_PREVIEW_LENGTH = 60


admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "slug", "posts_count")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request: HttpRequest) -> QuerySet[Category]:
        return super().get_queryset(request).annotate(posts_count=Count("posts"))

    @display(description="Posts", ordering="posts_count")
    def posts_count(self, obj: Category) -> int:
        return obj.posts_count


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ("name", "slug", "posts_count")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request: HttpRequest) -> QuerySet[Tag]:
        return super().get_queryset(request).annotate(posts_count=Count("posts"))

    @display(description="Posts", ordering="posts_count")
    def posts_count(self, obj: Tag) -> int:
        return obj.posts_count


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ("post", "author", "short_body", "created_at")
    list_select_related = ("post", "author")
    search_fields = ("body", "author__email", "post__title")
    autocomplete_fields = ("post", "author")
    list_filter_submit = True
    list_filter = (
        ("post", AutocompleteSelectFilter),
        ("author", AutocompleteSelectFilter),
        ("created_at", RangeDateTimeFilter),
    )

    @display(description="Comment")
    def short_body(self, obj: Comment) -> str:
        if len(obj.body) <= COMMENT_PREVIEW_LENGTH:
            return obj.body
        return f"{obj.body[:COMMENT_PREVIEW_LENGTH]}…"


class CommentInline(TabularInline):
    model = Comment
    fields = ("author", "body", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("author",)
    extra = 0
    tab = True
    per_page = 10


@admin.action(description="Publish selected posts")
def publish_selected(
    modeladmin: ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[Post],
) -> None:
    updated = queryset.update(status=Post.Status.PUBLISHED)
    modeladmin.message_user(
        request,
        f"{updated} post(s) published.",
        messages.SUCCESS,
    )


@admin.action(description="Move selected posts to drafts")
def unpublish_selected(
    modeladmin: ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[Post],
) -> None:
    updated = queryset.update(status=Post.Status.DRAFT)
    modeladmin.message_user(
        request,
        f"{updated} post(s) moved to drafts.",
        messages.SUCCESS,
    )


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = (
        "header",
        "status_label",
        "category",
        "tags_list",
        "comments_count",
        "created_at",
    )
    list_select_related = ("author", "category")
    search_fields = ("title", "body", "author__email")
    autocomplete_fields = ("author", "category", "tags")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    inlines = (CommentInline,)
    actions = (publish_selected, unpublish_selected)
    list_filter_submit = True
    list_filter = (
        ("status", ChoicesDropdownFilter),
        ("category", RelatedDropdownFilter),
        ("tags", MultipleRelatedDropdownFilter),
        ("author", AutocompleteSelectFilter),
        ("created_at", RangeDateTimeFilter),
    )
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }
    warn_unsaved_form = True

    fieldsets = (
        ("Content", {"classes": ("tab",), "fields": ("title", "slug", "body")}),
        (
            "Classification",
            {"classes": ("tab",), "fields": ("category", "tags", "status")},
        ),
        (
            "Meta",
            {"classes": ("tab",), "fields": ("author", "created_at", "updated_at")},
        ),
    )

    actions_row = ("toggle_status",)
    actions_list = ("publish_all_drafts",)
    actions_detail = ("open_comments",)
    actions_submit_line = ("save_and_publish",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Post]:
        return (
            super()
            .get_queryset(request)
            .select_related("author", "category")
            .prefetch_related("tags", "comments")
            .annotate(comments_count=Count("comments", distinct=True))
        )

    @display(description="Post", header=True)
    def header(self, obj: Post) -> tuple[str, str, str]:
        return obj.title, obj.author.email, ""

    @display(
        description="Status",
        label={"published": "success", "draft": "warning"},
    )
    def status_label(self, obj: Post) -> tuple[str, str]:
        return obj.status, obj.get_status_display()

    @display(description="Tags")
    def tags_list(self, obj: Post) -> str:
        return ", ".join(tag.name for tag in obj.tags.all()) or "—"

    @display(description="Comments", ordering="comments_count")
    def comments_count(self, obj: Post) -> int:
        return obj.comments_count

    @action(description="Publish")
    def toggle_status(self, request: HttpRequest, object_id: int) -> HttpResponse:
        post = self.get_object(request, object_id)
        post.status = (
            Post.Status.DRAFT
            if post.status == Post.Status.PUBLISHED
            else Post.Status.PUBLISHED
        )
        post.save(update_fields=("status", "updated_at"))
        return redirect(reverse("admin:blog_post_changelist"))

    @action(description="Publish all drafts")
    def publish_all_drafts(self, request: HttpRequest) -> HttpResponse:
        updated = Post.objects.filter(status=Post.Status.DRAFT).update(
            status=Post.Status.PUBLISHED,
        )
        self.message_user(request, f"{updated} draft(s) published.")
        return redirect(reverse("admin:blog_post_changelist"))

    @action(description="Open comments")
    def open_comments(self, request: HttpRequest, object_id: int) -> HttpResponse:
        url = f"{reverse('admin:blog_comment_changelist')}?post__id__exact={object_id}"
        return redirect(url)

    @action(description="Save & publish")
    def save_and_publish(self, request: HttpRequest, object_id: int) -> HttpResponse:
        post = self.get_object(request, object_id)
        post.status = Post.Status.PUBLISHED
        post.save(update_fields=("status", "updated_at"))
        return redirect(reverse("admin:blog_post_change", args=[object_id]))
