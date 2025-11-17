from django.contrib import admin
from .models import Profile, ProfilePrivacy, Message
from users.models import CustomUser

# Register your models here.

class ProfilePrivacyInline(admin.StackedInline):
    model = ProfilePrivacy
    can_delete = False
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'headline')
    search_fields = ('user__username', 'headline')
    list_filter = ('user__is_active', 'user__is_staff')
    inlines = [ProfilePrivacyInline]

@admin.register(ProfilePrivacy)
class ProfilePrivacyAdmin(admin.ModelAdmin):
    list_display = ['profile', 'is_profile_visible', 'updated_at']
    list_filter = ['is_profile_visible', 'updated_at']
    search_fields = ['user__username', 'user__email']

    def save_model(self, request, obj, form, change):
        if obj.is_superuser:
            obj.role = CustomUser.Role.ADMIN
        super().save_model(request, obj, form, change)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'created_at', 'in_app')
    search_fields = ('sender__username', 'recipient__username', 'text')
    list_filter = ('in_app', 'created_at')
    readonly_fields = ('created_at',)
    fields = ('sender', 'recipient', 'job', 'text', 'in_app', 'created_at')
