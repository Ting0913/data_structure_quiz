from django.db import models

class Question(models.Model):
    content = models.TextField(verbose_name="題目內容")
    def __str__(self):
        return self.content

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=255, verbose_name="選項內容")
    is_correct = models.BooleanField(default=False, verbose_name="正確答案")