from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('quiz/', views.quiz_home, name='quiz_home'),
    path('calculate/', views.calculate_score, name='calculate_score'),
    
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # 💡 這是先前增加的錯題本網址
    path('mistakes/', views.mistake_book, name='mistake_book'),

    # 🚀 這是最後一步要新增的：測驗紀錄詳情回顧網址！
    # <int:record_id> 代表它會自動去抓那一筆測驗紀錄的 ID
    path('record/<int:record_id>/', views.record_detail, name='record_detail'),
]