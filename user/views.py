# views.py
from rest_framework import viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from user.models import FriendRequest, User
from user.serializers import FriendRequestSerializer, UserSerializer
from django.db import models
import random

class FriendRequestViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset         = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # show only your sent or received requests
        return FriendRequest.objects.filter(
            models.Q(from_user=user) | models.Q(to_user=user)
        )

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        fr = self.get_object()
        if fr.to_user != request.user or fr.status != fr.PENDING:
            return Response({'detail': 'Not allowed'}, status=403)
        fr.accept()
        return Response({'status': 'accepted'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        fr = self.get_object()
        if fr.to_user != request.user or fr.status != fr.PENDING:
            return Response({'detail': 'Not allowed'}, status=403)
        fr.reject()
        return Response({'status': 'rejected'})


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """ GET /users/me/ """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def connections(self, request):
        """ GET /users/friends/ """
        qs = request.user.connections.all()
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page or qs, many=True)
        return self.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def show_random_users(self, request):
        user = request.user

        # 1. Get friends
        connections = user.connections.all()
        print(connections)
        # 2. Get IDs from pending friend requests (sent or received)
        sent_requests     = FriendRequest.objects.filter(from_user=user, status=FriendRequest.PENDING).values_list('to_user', flat=True)
        received_requests = FriendRequest.objects.filter(to_user=user,   status=FriendRequest.PENDING).values_list('from_user', flat=True)

        excluded_ids = set(
            connections.values_list('id', flat=True)
        ).union(sent_requests).union(received_requests).union([user.id])

        # 3. Exclude those users
        candidates = User.objects.exclude(id__in=excluded_ids)
        print(candidates)
        # 4. Randomly pick (e.g., 5 users)
        candidate_ids = list(candidates.values_list('id', flat=True))
        selected_ids = random.sample(candidate_ids, min(len(candidate_ids), 3))
        selected_users = User.objects.filter(id__in=selected_ids)
        print(selected_users)
        serializer = self.get_serializer(selected_users, many=True)
        return Response(serializer.data)
