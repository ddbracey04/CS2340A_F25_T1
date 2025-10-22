from django.contrib import admin
from .models import JobSeekerProfile, ProfilePrivacy

class ProfilePrivacyInline(admin.StackedInline):
    model = ProfilePrivacy
    can_delete = False

@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'location', 'experience_years']
    search_fields = ['full_name', 'email']
    inlines = [ProfilePrivacyInline]

@admin.register(ProfilePrivacy)
class ProfilePrivacyAdmin(admin.ModelAdmin):
    list_display = ['profile', 'is_profile_visible', 'updated_at']
    list_filter = ['is_profile_visible', 'updated_at']
    search_fields = ['profile__full_name']