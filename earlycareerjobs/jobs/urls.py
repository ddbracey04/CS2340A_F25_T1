from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='jobs.index'),
    path('new/', views.create_job, name='jobs.create'),
    path('<int:id>/edit/', views.edit_job, name='jobs.edit'),
    path('<int:id>/', views.show, name='jobs.show'),
    path('<int:id>/application/start/', views.start_application, name='jobs.start_application'),
]
