from django.urls import path, include
from .import views

urlpatterns = [
    path('', views.index, name='home.index'),
    path('index.html', views.index, name='home.index.html'),
    path('profile/edit/', views.profile_edit, name='profile.edit'),
    path('profile/<str:username>/', views.profile_detail, name='profile.detail'),
    # path('register.html', views.register, name='accounts.register.html'),
    # path('login.html', views.register, name='accounts.login.html'),
]