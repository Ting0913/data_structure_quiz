from django.contrib import admin
from django.urls import path
from quiz import views  # 引入 quiz 的 views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.quiz_home, name='quiz_home'), 
    path('submit/', views.calculate_score, name='calculate_score'), 
]