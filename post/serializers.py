from rest_framework import serializers
from post.models import Post, PostImage, Like, Comment
from django.contrib.auth import get_user_model

class SimpleUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(
        method_name='get_current_user_name')

    class Meta:
        model = get_user_model()
        fields = ['id', 'name']

    def get_current_user_name(self, obj):
        return obj.get_full_name()

class PostImageSerializer(serializers.ModelSerializer):
    images = serializers.ImageField()
    class Meta:
        model = PostImage
        fields = ['id', 'images']

class PostSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(method_name='get_user')
    images = PostImageSerializer(many=True, read_only=True)
    total_likes = serializers.SerializerMethodField(method_name='get_total_likes')
    total_comments = serializers.SerializerMethodField(method_name='get_total_comments')

    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'images', 'video_url', 'total_likes', 'total_comments', 'created_at', 'updated_at']
        read_only_fields = ['user', 'total_likes', 'total_comments']

    def get_user(self, obj):
        return SimpleUserSerializer(obj.user).data

    def get_total_likes(self, obj):
        return obj.likes.count()
    
    def get_total_comments(self, obj):
        return obj.comments.count()

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(method_name='get_user')
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'text', 'created_at']
        read_only_fields = ['user', 'post']

    def get_user(self, obj):
        return SimpleUserSerializer(obj.user).data

    def create(self, validated_data):
        post_id = self.context['post_id']
        return Comment.objects.create(post_id=post_id, **validated_data)

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['user', 'created_at', 'post']

    def get_user(self, obj):
        return SimpleUserSerializer(obj.user).data
    
    def create(self, validated_data):
        post_id = self.context['post_id']
        return Like.objects.create(post_id=post_id, **validated_data)