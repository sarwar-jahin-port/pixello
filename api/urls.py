from django.urls import path, include
from rest_framework_nested import routers
from post.views import PostViewSet, CommentViewSet, LikeViewSet, PostImageViewSet

router = routers.DefaultRouter()
router.register('posts', PostViewSet, basename='post')

posts_router = routers.NestedDefaultRouter(router, 'posts', lookup='post')
posts_router.register('comments', CommentViewSet, basename='post-comments')
posts_router.register('likes', LikeViewSet, basename='post-likes')
posts_router.register('images', PostImageViewSet, basename='post-images')
urlpatterns = [
    path('', include(router.urls)),
    path('', include(posts_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
