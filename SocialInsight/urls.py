from django.urls import path
from . import views

urlpatterns = [
    path('question/', views.question_view, name='question_view'),
    path('check_result/', views.check_result, name='check_result'),
    path('radar_chart/<int:session_id>/', views.radar_chart_image, name='radar_chart_image'),
]
