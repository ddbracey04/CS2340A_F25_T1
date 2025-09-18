from django.urls import path, include
from .import views

urlpatterns = [
    path('', views.index, name='home.index'),
    path('index.html', views.index, name='home.index.html'),
]