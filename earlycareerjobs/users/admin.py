from django.contrib import admin
from .models import CustomUser, ProfilePrivacy

class ProfilePrivacyInline(admin.StackedInline):
    model = ProfilePrivacy
    can_delete = False

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'phone_number']
    search_fields = ['username', 'email']
    list_filter = ['role']
    inlines = [ProfilePrivacyInline]

@admin.register(ProfilePrivacy)
class ProfilePrivacyAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_profile_visible', 'updated_at']
    list_filter = ['is_profile_visible', 'updated_at']
    search_fields = ['user__username', 'user__email']