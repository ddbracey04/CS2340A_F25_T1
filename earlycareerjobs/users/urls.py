
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('register/', views.register, name='users.register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='users.login'),
    path('logout/', auth_views.LogoutView.as_view(), name='users.logout'),
    path('admin/users/', views.user_management, name='users.user_management'),
    path('admin/users/<int:user_id>/edit/', views.edit_user, name='users.edit_user'),
    path('admin/users/<int:user_id>/toggle-status/', views.toggle_user_status, name='users.toggle_user_status'),
    path('privacy/', views.privacy_settings, name='privacy_settings'),
]