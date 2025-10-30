from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='jobs.index'),
    path('new/', views.create_job, name='jobs.create'),
    path('<int:id>/edit/', views.edit_job, name='jobs.edit'),
    path('<int:id>/', views.show, name='jobs.show'),
    path('<int:id>/update/<str:field>/', views.update_job_field, name='jobs.update_field'),
    path('<int:id>/application/start/', views.start_application, name='jobs.start_application'),
    path('<int:id>/delete/', views.delete_job, name='jobs.delete'),
    path('<int:job_id>/applicant/<int:app_id>/delete/', views.delete_applicant, name='jobs.delete_applicant'),
    path('<int:job_id>/applicant/<int:app_id>/edit/', views.edit_applicant, name='jobs.edit_applicant'),
    path('<int:id>/applications/', views.application_list, name='jobs.application_list'),
    path('<int:id>/applications/track/', views.track_applications, name='jobs.track_applications'),
    path('applications/<int:application_id>/update_status/<str:new_status>', views.update_application_status, name='jobs.update_application_status'),
    path('applications/<int:application_id>/ajax/update_status/', views.update_application_status_ajax, name='jobs.update_application_status_ajax'),
    path('recommendations/hide/', views.hide_recommendations, name='jobs.recommendations.hide'),
    path('recommendations/show/', views.show_recommendations, name='jobs.recommendations.show'),
]
