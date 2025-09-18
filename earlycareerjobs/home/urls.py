from django.urls import path, include
from .import views

urlpatterns = [
    path('', views.index, name='home.index'),
    path('index.html', views.index, name='home.index.html'),
    # path('register.html', views.register, name='accounts.register.html'),
    # path('login.html', views.register, name='accounts.login.html'),
]