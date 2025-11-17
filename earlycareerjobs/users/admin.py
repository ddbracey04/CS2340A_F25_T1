from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

#reusing action from jobs app
from jobs.admin import export_as_csv

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    actions = [export_as_csv]
    list_display = UserAdmin.list_display + ('role', 'company_name')
    list_filter = UserAdmin.list_filter + ('role',)
    fieldsets = UserAdmin.fieldsets + (('Extra Info', {'fields': ('role', 'company_name')}),)