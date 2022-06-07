from django.urls import path
from . import views

urlpatterns = [
    path('my_profile/', views.profile, name='my-profile'),
]
