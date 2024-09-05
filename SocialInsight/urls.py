from django.urls import path
from . import views

urlpatterns = [
    path('question/', views.question_view, name='question_view'),
]
