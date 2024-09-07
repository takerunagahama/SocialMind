from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('sq_detail/', views.sq_detail, name='sq_detail'),
    path('about/', views.about_view, name='about'),
    path('signup/', views.signup_view, name='signup'),
]