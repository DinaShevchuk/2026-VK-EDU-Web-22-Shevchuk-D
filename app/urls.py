from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<slug:tag_name>/', views.tag, name='tag'),
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
]
