"""
Serializers for core app
"""
from django.db import models
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from .models import User, UserProfile, UserCourseProgress


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['learning_language', 'current_hsk_level', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UserCourseProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCourseProgress
        fields = [
            'current_day', 'current_lesson', 'current_step',
            'total_xp', 'streak_days', 'last_study_date',
            'completed_days', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(BaseUserSerializer):
    profile = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    likes_received = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = [
            'id', 'username', 'email', 'profile', 'progress',
            'followers_count', 'following_count', 'likes_received',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_profile(self, obj):
        """Safely get user profile - create if missing"""
        try:
            # Try to get existing profile
            from .models import UserProfile
            profile, created = UserProfile.objects.get_or_create(
                user=obj,
                defaults={'learning_language': 'RU'}
            )

            if profile:
                return UserProfileSerializer(profile).data
        except Exception as e:
            # Log error but don't fail - return default
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting profile for user {obj.username}: {e}")

        # Return default if anything fails
        return {
            'learning_language': 'RU',
            'current_hsk_level': 1,
            'created_at': None,
            'updated_at': None
        }

    def get_progress(self, obj):
        """Safely get user progress - create if missing"""
        try:
            # Try to get existing progress
            from .models import UserCourseProgress
            progress, created = UserCourseProgress.objects.get_or_create(user=obj)

            if progress:
                return UserCourseProgressSerializer(progress).data
        except Exception as e:
            # Log error but don't fail - return default
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting progress for user {obj.username}: {e}")

        # Return default if anything fails
        return {
            'current_day': 1,
            'current_lesson': 1,
            'current_step': 1,
            'total_xp': 0,
            'streak_days': 0,
            'last_study_date': None,
            'completed_days': [],
            'created_at': None,
            'updated_at': None
        }

    def get_followers_count(self, obj):
        """Get count of users following this user"""
        # TODO: Implement following system
        return 0

    def get_following_count(self, obj):
        """Get count of users this user is following"""
        # TODO: Implement following system
        return 0

    def get_likes_received(self, obj):
        """Get total likes received on user's videos"""
        from video.models import Video
        try:
            total_likes = Video.objects.filter(user=obj).aggregate(
                total=models.Sum('likes_count')
            )['total'] or 0
            return total_likes
        except Exception:
            return 0


class UserCreateSerializer(BaseUserCreateSerializer):
    """
    Serializer for user registration with additional fields
    """
    learning_language = serializers.ChoiceField(
        choices=[('RU', 'Russian'), ('KZ', 'Kazakh')],
        default='RU',
        write_only=True,
        required=False
    )

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ['username', 'email', 'password', 'learning_language']

    def validate(self, attrs):
        """
        Remove learning_language before passing to parent validation
        """
        # Extract learning_language before validation
        self._learning_language = attrs.pop('learning_language', 'RU')
        # Call parent validation without learning_language
        return super().validate(attrs)

    def create(self, validated_data):
        """
        Create user with profile and progress
        Note: Profile and progress are automatically created by signals
        """
        user = super().create(validated_data)

        # Update profile with learning_language (signals will create if needed)
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'learning_language': self._learning_language}
        )
        if not created:
            profile.learning_language = self._learning_language
            profile.save()

        # Progress is automatically created by signals
        UserCourseProgress.objects.get_or_create(user=user)

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Detailed user serializer for profile endpoint
    """
    profile = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    likes_received = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'profile', 'progress', 'followers_count', 'following_count',
            'likes_received', 'date_joined'
        ]
        read_only_fields = ['date_joined']

    def get_profile(self, obj):
        """Safely get user profile - create if missing"""
        try:
            # Try to get existing profile
            from .models import UserProfile
            profile, created = UserProfile.objects.get_or_create(
                user=obj,
                defaults={'learning_language': 'RU'}
            )

            if profile:
                return UserProfileSerializer(profile).data
        except Exception as e:
            # Log error but don't fail - return default
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting profile for user {obj.username}: {e}")

        # Return default if anything fails
        return {
            'learning_language': 'RU',
            'current_hsk_level': 1,
            'created_at': None,
            'updated_at': None
        }

    def get_progress(self, obj):
        """Safely get user progress - create if missing"""
        try:
            # Try to get existing progress
            from .models import UserCourseProgress
            progress, created = UserCourseProgress.objects.get_or_create(user=obj)

            if progress:
                return UserCourseProgressSerializer(progress).data
        except Exception as e:
            # Log error but don't fail - return default
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting progress for user {obj.username}: {e}")

        # Return default if anything fails
        return {
            'current_day': 1,
            'current_lesson': 1,
            'current_step': 1,
            'total_xp': 0,
            'streak_days': 0,
            'last_study_date': None,
            'completed_days': [],
            'created_at': None,
            'updated_at': None
        }

    def get_followers_count(self, obj):
        """Get count of users following this user"""
        # TODO: Implement following system
        return 0

    def get_following_count(self, obj):
        """Get count of users this user is following"""
        # TODO: Implement following system
        return 0

    def get_likes_received(self, obj):
        """Get total likes received on user's videos"""
        from video.models import Video
        try:
            total_likes = Video.objects.filter(user=obj).aggregate(
                total=models.Sum('likes_count')
            )['total'] or 0
            return total_likes
        except Exception:
            return 0
