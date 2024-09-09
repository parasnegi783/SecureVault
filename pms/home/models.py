from django.db import models

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class UserOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_otp')
    otp = models.CharField(max_length=6, blank=True, null=True)  # Adjust the max_length as needed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - OTP: {self.otp}"


class UserPassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='passwords')
    site_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255,default=None)
    email = models.EmailField(max_length=255)  # New email field
    password = models.CharField(max_length=255)
    strength_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 85.50 for 85.5%

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.site_name} ({self.email}) ({self.strength_percentage}%)"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - Profile Photo"