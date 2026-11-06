import random
from datetime import timedelta
from time import perf_counter
from typing import Any

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from faker import Faker

from apps.auths.models import User
from apps.blog.models import Category, Comment, Post, Tag

DEFAULT_USERS = 20
DEFAULT_POSTS = 100
DEFAULT_COMMENTS = 500

SEED_PASSWORD = "Password123!"  

INACTIVE_USER_RATIO = 0.15
STAFF_USER_RATIO = 0.1

PUBLISHED_RATIO = 0.7
NO_CATEGORY_RATIO = 0.1
MIN_TAGS_PER_POST = 0
MAX_TAGS_PER_POST = 5
MIN_POST_PARAGRAPHS = 3
MAX_POST_PARAGRAPHS = 6
MIN_COMMENT_SENTENCES = 1
MAX_COMMENT_SENTENCES = 3

SEED_HISTORY_START = "-1y"

CATEGORY_NAMES = [
    "Python",
    "Django",
    "DevOps",
    "Frontend",
    "Backend",
    "Databases",
    "Testing",
    "Machine Learning",
]

TAG_NAMES = [
    "REST API",
    "Docker",
    "Kubernetes",
    "PostgreSQL",
    "Redis",
    "Celery",
    "CI/CD",
    "Linux",
    "Git",
    "Security",
    "Performance",
    "Microservices",
    "GraphQL",
    "WebSockets",
    "Asyncio",
    "Unit Tests",
    "Deployment",
    "Monitoring",
    "Caching",
    "ORM",
]


class Command(BaseCommand):
    help = "Fill the database with fake data."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--users",
            type=int,
            default=DEFAULT_USERS,
            help="Number of users to create",
        )
        parser.add_argument(
            "--posts",
            type=int,
            default=DEFAULT_POSTS,
            help="Number of posts to create",
        )
        parser.add_argument(
            "--comments",
            type=int,
            default=DEFAULT_COMMENTS,
            help="Number of comments to create",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing data before seeding",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        users_count: int = options["users"]
        posts_count: int = options["posts"]
        comments_count: int = options["comments"]
        clear: bool = options["clear"]

        for flag, value in (
            ("--users", users_count),
            ("--posts", posts_count),
            ("--comments", comments_count),
        ):
            if value < 0:
                raise CommandError(f"{flag} must not be negative.")

        started_at = perf_counter()
        fake = Faker()

        if clear:
            self._clear_data()

        with transaction.atomic():
            categories, categories_created = self._seed_categories()
            tags, tags_created = self._seed_tags()
            self._seed_users(fake, users_count)

        authors = list(User.objects.all())
        if posts_count > 0 and not authors:
            raise CommandError("Cannot create posts: there are no users.")
        if comments_count > 0 and not authors:
            raise CommandError("Cannot create comments: there are no users.")

        with transaction.atomic():
            created_posts = self._seed_posts(
                fake,
                posts_count,
                authors,
                categories,
                tags,
            )

        published_posts = list(
            Post.objects.filter(status=Post.Status.PUBLISHED),
        )
        if comments_count > 0 and not published_posts:
            raise CommandError(
                "Cannot create comments: there are no published posts.",
            )

        with transaction.atomic():
            created_comments = self._seed_comments(
                fake,
                comments_count,
                authors,
                published_posts,
            )

        elapsed = perf_counter() - started_at

        self.stdout.write(self.style.SUCCESS(f"Users: {users_count} created"))
        self.stdout.write(
            self.style.SUCCESS(f"Categories: {categories_created} created"),
        )
        self.stdout.write(self.style.SUCCESS(f"Tags: {tags_created} created"))
        self.stdout.write(
            self.style.SUCCESS(f"Posts: {len(created_posts)} created"),
        )
        self.stdout.write(
            self.style.SUCCESS(f"Comments: {len(created_comments)} created"),
        )
        self.stdout.write(self.style.SUCCESS(f"Done in {elapsed:.2f} seconds"))

    def _clear_data(self) -> None:
        Comment.objects.all().delete()
        Post.objects.all().delete()
        Tag.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.WARNING("Existing data cleared."))

    def _seed_categories(self) -> tuple[list[Category], int]:
        existing_slugs = set(Category.objects.values_list("slug", flat=True))
        to_create = []

        for name in CATEGORY_NAMES:
            slug = slugify(name)
            if slug not in existing_slugs:
                to_create.append(Category(name=name, slug=slug))
                existing_slugs.add(slug)

        Category.objects.bulk_create(to_create)

        return list(Category.objects.all()), len(to_create)

    def _seed_tags(self) -> tuple[list[Tag], int]:
        existing_slugs = set(Tag.objects.values_list("slug", flat=True))
        to_create = []

        for name in TAG_NAMES:
            slug = slugify(name)
            if slug not in existing_slugs:
                to_create.append(Tag(name=name, slug=slug))
                existing_slugs.add(slug)

        Tag.objects.bulk_create(to_create)

        return list(Tag.objects.all()), len(to_create)

    def _seed_users(self, fake: Faker, users_count: int) -> None:
        if users_count == 0:
            return

        existing_emails = set(User.objects.values_list("email", flat=True))
        hashed_password = make_password(SEED_PASSWORD)

        new_users = []
        for _ in range(users_count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = self._unique_email(first_name, last_name, existing_emails)

            new_users.append(
                User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=hashed_password,
                    is_active=random.random() > INACTIVE_USER_RATIO,
                    is_staff=random.random() < STAFF_USER_RATIO,
                ),
            )

        User.objects.bulk_create(new_users)

    @staticmethod
    def _unique_email(
        first_name: str,
        last_name: str,
        existing_emails: set[str],
    ) -> str:
        base = f"{first_name}.{last_name}".lower()
        email = f"{base}@example.com"
        suffix = 2

        while email in existing_emails:
            email = f"{base}{suffix}@example.com"
            suffix += 1

        existing_emails.add(email)
        return email

    def _seed_posts(
        self,
        fake: Faker,
        posts_count: int,
        authors: list[User],
        categories: list[Category],
        tags: list[Tag],
    ) -> list[Post]:
        if posts_count == 0:
            return []

        existing_slugs = set(Post.objects.values_list("slug", flat=True))
        max_tags = min(MAX_TAGS_PER_POST, len(tags))

        new_posts = []
        tags_per_post: list[list[Tag]] = []

        for _ in range(posts_count):
            title = fake.sentence(nb_words=6).rstrip(".")
            slug = self._unique_slug(title, existing_slugs)
            created_at = fake.date_time_between(
                start_date=SEED_HISTORY_START,
                end_date="now",
                tzinfo=timezone.get_current_timezone(),
            )
            status = (
                Post.Status.PUBLISHED
                if random.random() < PUBLISHED_RATIO
                else Post.Status.DRAFT
            )
            category = (
                None
                if random.random() < NO_CATEGORY_RATIO
                else random.choice(categories)
            )
            paragraphs_count = random.randint(
                MIN_POST_PARAGRAPHS,
                MAX_POST_PARAGRAPHS,
            )
            body = "\n\n".join(fake.paragraphs(nb=paragraphs_count))

            new_posts.append(
                Post(
                    author=random.choice(authors),
                    title=title,
                    slug=slug,
                    body=body,
                    category=category,
                    status=status,
                    created_at=created_at,
                    updated_at=created_at,
                ),
            )
            tags_per_post.append(
                random.sample(tags, k=random.randint(MIN_TAGS_PER_POST, max_tags)),
            )

        created_posts = Post.objects.bulk_create(new_posts)

        for post, post_tags in zip(created_posts, tags_per_post, strict=True):
            post.tags.set(post_tags)

        return created_posts

    @staticmethod
    def _unique_slug(title: str, existing_slugs: set[str]) -> str:
        base_slug = slugify(title)
        slug = base_slug
        suffix = 2

        while slug in existing_slugs:
            slug = f"{base_slug}-{suffix}"
            suffix += 1

        existing_slugs.add(slug)
        return slug

    def _seed_comments(
        self,
        fake: Faker,
        comments_count: int,
        authors: list[User],
        published_posts: list[Post],
    ) -> list[Comment]:
        if comments_count == 0:
            return []

        now = timezone.now()
        new_comments = []

        for _ in range(comments_count):
            post = random.choice(published_posts)
            max_delay = max(int((now - post.created_at).total_seconds()), 1)
            created_at = post.created_at + timedelta(
                seconds=random.randint(0, max_delay),
            )
            sentences_count = random.randint(
                MIN_COMMENT_SENTENCES,
                MAX_COMMENT_SENTENCES,
            )

            new_comments.append(
                Comment(
                    post=post,
                    author=random.choice(authors),
                    body=" ".join(fake.sentences(nb=sentences_count)),
                    created_at=created_at,
                ),
            )

        return Comment.objects.bulk_create(new_comments)