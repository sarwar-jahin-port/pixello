from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from post.models import Post, Comment, Like, PostImage
from post.serializers import PostSerializer, CommentSerializer, LikeSerializer, PostImageSerializer
from post.permissions import IsPostAuthorOrReadonly, IsCommentAuthorOrReadOnly, IsLikeAuthor
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from post.paginations import DefaultPagination
from api.permissions import IsAdminOrReadOnly

# Create your views here.

class PostViewSet(ModelViewSet):
    '''
    API endpoint for managing blog posts.

    list:
    Get all posts (filtered, ordered, and paginated).

    create:
    Create a new post (authenticated users only).

    retrieve:
    Get a specific post by ID.

    update:
    Update an existing post (post author only).

    partial_update:
    Partially update a post (post author only).

    destroy:
    Delete a post (post author only).

    search_fields:
    - content: Search by post content
    - user__username: Search by username

    ordering_fields:
    - id: Order by creation date (descending default)
    '''
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsPostAuthorOrReadonly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    pagination_class = DefaultPagination
    search_fields = ['content', 'user']
    OrderingFilter = ['-id',]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PostImageViewSet(ModelViewSet):
    '''
    API endpoint for managing post images (nested under posts).

    list:
    Get all images for a specific post.

    create:
    Add an image to a post (admin users only).

    retrieve:
    Get a specific post image.

    destroy:
    Remove an image from a post (admin users only).

    Path Parameters:
    - post_pk: ID of the parent post
    '''
    serializer_class = PostImageSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return PostImage.objects.filter(post_id=self.kwargs.get('post_pk'))

    def perform_create(self, serializer):
        serializer.save(post_id=self.kwargs.get('post_pk'))

class CommentViewSet(ModelViewSet):
    '''
    API endpoint for managing post comments (nested under posts).

    list:
    Get all comments for a specific post.

    create:
    Add a comment to a post (authenticated users only).

    retrieve:
    Get a specific comment.

    update:
    Update a comment (comment author only).

    partial_update:
    Partially update a comment (comment author only).

    destroy:
    Delete a comment (comment author only).

    Path Parameters:
    - post_pk: ID of the parent post
    '''
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsCommentAuthorOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs.get('post_pk'))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_context(self):
        return {'post_id': self.kwargs.get('post_pk')}

class LikeViewSet(ModelViewSet):
    '''
    API endpoint for managing post likes (nested under posts).

    list:
    Get all likes for a specific post.

    create:
    Like a post (authenticated users only).

    destroy:
    Remove a like from a post (like owner only).

    Path Parameters:
    - post_pk: ID of the parent post
    '''
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated, IsLikeAuthor]
    http_method_names = ['get', 'post', 'delete']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Like.objects.filter(post_id=self.kwargs.get('post_pk'))
    
    def get_serializer_context(self):
        return {'post_id': self.kwargs.get('post_pk')}