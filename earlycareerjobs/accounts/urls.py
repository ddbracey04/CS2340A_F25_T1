from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('register.html', views.register, name='accounts.register.html'),
    # path('login.html', views.register, name='accounts.register.html'),
    
    # path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    # path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html', success_url='/'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page = '/'), name='logout'),
]