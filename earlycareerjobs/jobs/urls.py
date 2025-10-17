from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='jobs.index'),
    path('new/', views.create_job, name='jobs.create'),
    path('<int:id>/edit/', views.edit_job, name='jobs.edit'),
    path('<int:id>/', views.show, name='jobs.show'),
    path('<int:id>/application/start/', views.start_application, name='jobs.start_application'),

    path('<int:id>/applications/', views.application_list, name='jobs.application_list'),
    path('<int:id>/applications/track/', views.track_applications, name='jobs.track_applications'),
    path('<int:id>/applications/update_status/<int:application_id>/', views.update_application_status, name='jobs.update_application_status'),
]
