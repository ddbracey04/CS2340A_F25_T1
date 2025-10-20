from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='jobs.index'),
    path('new/', views.create_job, name='jobs.create'),
    path('<int:id>/edit/', views.edit_job, name='jobs.edit'),
    path('<int:id>/', views.show, name='jobs.show'),
    path('<int:id>/application/start/', views.start_application, name='jobs.start_application'),
    path('<int:id>/delete/', views.delete_job, name='jobs.delete'),
    path('<int:job_id>/applicant/<int:app_id>/delete/', views.delete_applicant, name='jobs.delete_applicant'),
    path('<int:job_id>/applicant/<int:app_id>/edit/', views.edit_applicant, name='jobs.edit_applicant'),
]
