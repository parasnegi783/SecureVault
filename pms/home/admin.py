from django.contrib import admin
from django.utils.html import format_html  # To display HTML (like image tags) in the admin panel
from .models import UserProfile, UserPassword, UserOTP

# Custom UserProfileAdmin to display photo
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_photo')  # Display the user and profile photo

    def display_photo(self, obj):
        if obj.photo:
            # Display the photo as an HTML img tag
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;" />', obj.photo.url)
        else:
            return "No Photo"
    display_photo.short_description = 'Profile Photo'  # Customize the column name

# Customize UserPassword in admin
class UserPasswordAdmin(admin.ModelAdmin):
    list_display = ('user', 'site_name', 'email', 'strength_percentage', 'created_at')
    search_fields = ('user__username', 'site_name', 'email')  # Searchable fields
    list_filter = ('user', 'created_at')  # Filter by user and created date
    ordering = ('-created_at',)  # Order by newest password entries first

# Customize UserOTP in admin
class UserOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp', 'created_at')
    search_fields = ('user__username', 'otp')  # Search by username or OTP
    list_filter = ('created_at',)  # Filter by creation date

# Register the models with the admin site
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserPassword, UserPasswordAdmin)
admin.site.register(UserOTP, UserOTPAdmin)
