from django.urls import path, include
from rest_framework_nested import routers
from post.views import PostViewSet, CommentViewSet, LikeViewSet, PostImageViewSet
from api import views

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
    path('payment/initiate/', views.InitiatePaymentAPIView.as_view(), name="initiate_payment"),
    path('payment/success/', views.payment_success, name="payment_success"),
    path('payment/failed/', views.payment_failed, name="payment_failed"),
    path('payment/cancelled/', views.payment_cancelled, name="payment_cancelled")
]
