from django.urls import path
from . import views

urlpatterns = [
    path('start_diagnosis/', views.start_diagnosis_view, name='start_diagnosis'),
    path('question/', views.question_view, name='question_view'),
    path('check_result/', views.check_result, name='check_result'),
    path('radar_chart/<int:session_id>/', views.radar_chart_image, name='radar_chart_image'),
    path('answer_list/<int:session_id>/', views.answer_list_view, name='answer_list'),
    path('diagnosis_complete/', views.diagnosis_complete, name='diagnosis_complete'),
    path('result_scores/<int:session_id>', views.get_bert_scores, name='get_bert_scores')
]
