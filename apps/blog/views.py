from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from apps.blog.models import Category, Comment, Post, Tag
from apps.blog.permissions import IsOwnerOrReadOnly
from apps.blog.serializers import (
    CategorySerializer,
    CommentSerializer,
    PostSerializer,
    TagSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related(
        "author",
        "category",
    ).prefetch_related("tags")
    serializer_class = PostSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def perform_create(self, serializer: PostSerializer) -> None:
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related(
        "author",
        "post",
    )
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def perform_create(self, serializer: CommentSerializer) -> None:
        serializer.save(author=self.request.user)
