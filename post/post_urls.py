from django.urls import path
from post import views

urlpatterns = [
    path('', views.PostViewSet.as_view({'get': 'list', 'post': 'create'}), name='post-list'),
    path('<int:pk>/', views.PostViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update', 
        'patch': 'partial_update', 
        'delete': 'destroy'
    }), name='post-detail'),
]