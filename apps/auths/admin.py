from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import BooleanRadioFilter
from unfold.decorators import action, display

from apps.auths.forms import UserChangeForm, UserCreationForm
from apps.auths.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    ordering = ("email",)
    list_display = ("header", "status_label", "staff_label", "posts_count")
    search_fields = ("email", "first_name", "last_name")
    list_filter = (
        ("is_active", BooleanRadioFilter),
        ("is_staff", BooleanRadioFilter),
    )
    actions = ("activate_users", "deactivate_users")
    filter_horizontal = ("groups", "user_permissions")

    fieldsets = (
        (
            "Personal info",
            {
                "classes": ("tab",),
                "fields": ("email", "first_name", "last_name", "password"),
            },
        ),
        (
            "Permissions",
            {
                "classes": ("tab",),
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"classes": ("tab",), "fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("tab",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[User]:
        return super().get_queryset(request).annotate(posts_count=Count("posts"))

    @display(description="User", header=True)
    def header(self, obj: User) -> tuple[str, str, str]:
        initials = f"{obj.first_name[:1]}{obj.last_name[:1]}".upper()
        return f"{obj.first_name} {obj.last_name}", obj.email, initials

    @display(description="Active", label={True: "success", False: "danger"})
    def status_label(self, obj: User) -> tuple[bool, str]:
        return obj.is_active, "Active" if obj.is_active else "Inactive"

    @display(description="Staff", label={True: "info", False: "secondary"})
    def staff_label(self, obj: User) -> tuple[bool, str]:
        return obj.is_staff, "Staff" if obj.is_staff else "User"

    @display(description="Posts", ordering="posts_count")
    def posts_count(self, obj: User) -> int:
        return obj.posts_count

    @action(description="Activate selected users")
    def activate_users(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} user(s) activated.", messages.SUCCESS)

    @action(description="Deactivate selected users")
    def deactivate_users(
        self,
        request: HttpRequest,
        queryset: QuerySet[User],
    ) -> None:
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f"{updated} user(s) deactivated.",
            messages.SUCCESS,
        )
