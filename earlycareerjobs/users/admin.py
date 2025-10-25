from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'phone_number']
    search_fields = ['username', 'email']
    list_filter = ['role']

#admin.site.register(CustomUser, CustomUserAdmin)