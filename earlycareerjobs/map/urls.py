from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='map.index'),
    path('<str:lat>/<str:lon>', views.indexLatLon, name='map.indexLatLon'),
    path('select_location', views.select_location, name='map.select_location'),
    path('filter', views.filter, name='map.filter'),
    path('noFilter', views.indexNoFilter, name='map.noFilter'),
]