from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer
from rest_framework import serializers
from .models import User, FriendRequest

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'email', 'password', 'first_name',
                  'last_name', 'phone', 'location', 'premium']


class UserSerializer(BaseUserSerializer):
    friends = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta(BaseUserSerializer.Meta):
        ref_name = 'CustomUser'
        fields = ['id', 'username', 'email', 'first_name',
                  'last_name', 'phone', 'location', 'premium', 'friends']

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'location']

class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserBasicSerializer(read_only=True)
    to_user   = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    to_user_data = UserBasicSerializer(source='to_user', read_only=True)

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    class Meta:
        model  = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'to_user_data', 'status', 'status_display', 'created']
        read_only_fields = ['from_user', 'to_user_data', 'status_display']

    def create(self, validated_data):
        # The from_user will be set in the view's perform_create method
        return super().create(validated_data)

    def to_representation(self, instance):
        """Custom representation for different contexts"""
        data = super().to_representation(instance)
        
        # Remove the write-only to_user field from response
        data.pop('to_user', None)
        
        # Rename to_user_data to to_user for consistency
        if 'to_user_data' in data:
            data['to_user'] = data.pop('to_user_data')
            
        return data
