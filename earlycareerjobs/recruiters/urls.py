from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='recruiters.index'),
    path('<int:id>/', views.show, name='recruiters.show'),
    path('<int:id>/application/start/', views.start_application, name='recruiters.start_application'),
]