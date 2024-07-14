# models.py
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, blank=True, null=True)

# Link UserProfile to User
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
