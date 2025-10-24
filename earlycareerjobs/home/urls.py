from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='home.index'),
    path('about', views.about, name='home.about'),
    path('profile/edit/', views.profile_edit, name='profile.edit'),
    path('profile/education/save/', views.save_education, name='save_education_add'),
    path('profile/education/save/<int:education_id>/', views.save_education, name='save_education_edit'),
    path('profile/education/delete/<int:education_id>/', views.delete_education, name='delete_education'),
    path('profile/<str:username>/', views.profile_view, name='profile.view'),
    path('candidates/', views.search_candidates, name='candidates.search'),
    path('privacy/', views.privacy_settings, name='privacy_settings'),
]
