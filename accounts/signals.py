from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserBalance

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_related_models(sender, instance, created, **kwargs):
    # Only create related models if the user is newly created and not a superuser
    UserBalance.objects.get_or_create(user=instance)
    
    
 
 
 
 
    
    
    