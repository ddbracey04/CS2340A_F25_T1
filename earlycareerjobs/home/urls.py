from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='home.index'),
    path('about', views.about, name='home.about'),
    path('profile/edit/', views.profile_edit, name='profile.edit'),
    path('profile/<str:username>/', views.profile_view, name='profile.view'),
]