"""
Signals for user registration
Automatically creates UserProfile and UserCourseProgress when a User is created
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile, UserCourseProgress
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile_and_progress(sender, instance, created, **kwargs):
    """
    Create UserProfile and UserCourseProgress when a new User is created
    This ensures these objects always exist for every user
    """
    if created:
        logger.info(f"Creating profile and progress for new user: {instance.username}")

        # Create UserProfile if it doesn't exist
        profile, profile_created = UserProfile.objects.get_or_create(
            user=instance,
            defaults={'learning_language': 'RU'}
        )
        logger.info(f"UserProfile {'created' if profile_created else 'already exists'} for {instance.username}")

        # Create UserCourseProgress if it doesn't exist
        progress, progress_created = UserCourseProgress.objects.get_or_create(user=instance)
        logger.info(f"UserCourseProgress {'created' if progress_created else 'already exists'} for {instance.username}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the user profile when user is saved
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
        logger.info(f"Saved profile for user: {instance.username}")
