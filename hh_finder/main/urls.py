from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('search/', include('search.urls', namespace='search')),
    path('users/', include('users.urls'), name='users'),
]

