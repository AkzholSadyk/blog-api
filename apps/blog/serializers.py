from rest_framework import serializers

from apps.blog.models import Category, Comment, Post, Tag


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "slug",
        )


class PostSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(
        source="author.email",
        read_only=True,
    )
    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )
    tags = TagSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "author_email",
            "title",
            "slug",
            "body",
            "category",
            "category_name",
            "tags",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "author",
            "author_email",
            "created_at",
            "updated_at",
        )


class CommentSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(
        source="author.email",
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = (
            "id",
            "post",
            "author",
            "author_email",
            "body",
            "created_at",
        )
        read_only_fields = (
            "author",
            "author_email",
            "created_at",
        )
