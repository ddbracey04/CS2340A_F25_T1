from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
	fieldsets = (
		(None, {'fields': ('username', 'password')}),
		('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
		('Role Info', {'fields': ('role', 'company_name', 'resume')}),
		('Important dates', {'fields': ('last_login', 'date_joined')}),
		('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
	)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('username', 'email', 'password1', 'password2', 'role', 'company_name', 'resume', 'is_active', 'is_staff', 'is_superuser'),
		}),
	)
	list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
	list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
	exclude = ('groups', 'user_permissions')

	def save_model(self, request, obj, form, change):
		# 如果是新建超级用户，自动设为ADMIN
		if obj.is_superuser:
			obj.role = CustomUser.Role.ADMIN
		super().save_model(request, obj, form, change)

admin.site.register(CustomUser, CustomUserAdmin)
