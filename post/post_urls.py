from django.urls import path
from post import views

urlpatters = [
    path('', views.PostViewSet.as_view(), name='post-list'),
]