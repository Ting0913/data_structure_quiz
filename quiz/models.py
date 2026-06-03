from django.db import models
from django.contrib.auth.models import User  # 💡 匯入 Django 內建的會員模型

class Question(models.Model):
    content = models.TextField(verbose_name="題目內容")
    explanation = models.TextField(verbose_name="題目解析", blank=True, null=True, default="暫無解析。")
    
    def __str__(self):
        return self.content

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=255, verbose_name="選項內容")
    is_correct = models.BooleanField(default=False, verbose_name="正確答案")

class QuizRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_records')
    total_questions = models.IntegerField(verbose_name="總題數")       
    correct_count = models.IntegerField(verbose_name="答對題數")         
    score_percent = models.IntegerField(verbose_name="得分率")         
    duration = models.CharField(max_length=10, verbose_name="花費時間") 
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作答時間")  

    def __str__(self):
        return f"{self.user.username} - {self.score_percent}% ({self.total_questions}題)"

# 💡 QuizAnswer 必須與 QuizRecord 平行（靠最左邊開始寫）
class QuizAnswer(models.Model):
    # 這裡要縮排 4 格
    quiz_record = models.ForeignKey(QuizRecord, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_choice_text = models.CharField(max_length=255)
    is_correct = models.BooleanField()

    def __str__(self):
        # 這裡要縮排 8 格
        return f"{self.quiz_record.id} - {self.question.content[:10]}"