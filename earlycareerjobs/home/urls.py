from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='home.index'),
    path('about', views.about, name='home.about'),
    path('profile/edit/', views.profile_edit, name='profile.edit'),
    path('profile/education/save/', views.save_education, name='save_education_add'),
    path('profile/education/save/<int:education_id>/', views.save_education, name='save_education_edit'),
    path('profile/education/delete/<int:education_id>/', views.delete_education, name='delete_education'),
    path('profile/<str:username>/update/<str:field>/', views.update_profile_field, name='profile.update_field'),
    path('profile/<str:username>/', views.profile_view, name='profile.view'),
    path('candidates/', views.search_candidates, name='candidates.search'),
    path('privacy/', views.privacy_settings, name='privacy_settings'),
    path('saved-searches/', views.saved_searches, name='saved_searches'),
    path('saved-searches/delete/<int:search_id>/', views.delete_saved_search, name='delete_saved_search'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('message/', views.message_compiler, name='home.message_compiler'),
    path('api/usernames/', views.search_usernames, name='home.search_usernames'),
    path('inbox/', views.inbox, name='home.inbox'),
    path('inbox/mark-read/<int:message_id>/', views.mark_message_read, name='home.mark_message_read'),
]
