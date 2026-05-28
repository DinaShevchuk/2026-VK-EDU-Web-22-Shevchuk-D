from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<slug:tag_name>/', views.tag, name='tag'),
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
    path('ask/', views.ask_question, name='ask'),  # Добавлено
    path('question/<int:question_id>/answer/', views.add_answer, name='add_answer'),
    path('question/<int:question_id>/like/', views.like_question, name='like_question'),
    path('answer/<int:answer_id>/like/', views.like_answer, name='like_answer'),
    path('answer/<int:answer_id>/correct/', views.mark_correct_answer, name='mark_correct'),
]
