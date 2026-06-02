from django.shortcuts import render
from .models import Question, Choice

def quiz_home(request):
    questions = Question.objects.all()
    return render(request, 'quiz/quiz.html', {'questions': questions})

def calculate_score(request):
    if request.method == 'POST':
        correct_count = 0
        questions = Question.objects.all()
        total_questions = questions.count()
        detailed_results = [] 
        
        # 處理作答時間
        raw_seconds = request.POST.get('user_duration', '0')
        try:
            total_seconds = int(raw_seconds)
            mins = total_seconds // 60
            secs = total_seconds % 60
            duration_string = f"{mins:02d}:{secs:02d}"
        except ValueError:
            duration_string = "00:00"

        for index, q in enumerate(questions, start=1):
            user_choice_id = request.POST.get(f'q{q.id}')
            
            correct_choice = q.choices.filter(is_correct=True).first()
            correct_text = correct_choice.text if correct_choice else "未設定正確答案"
            
            user_choice_text = "未作答"
            is_correct = False
            
            if user_choice_id:
                try:
                    selected_choice = q.choices.get(id=int(user_choice_id))
                    user_choice_text = selected_choice.text
                    if selected_choice.is_correct: 
                        correct_count += 1
                        is_correct = True
                except Choice.DoesNotExist:
                    pass
            
            detailed_results.append({
                'number': index,
                'content': q.content,
                'user_answer': user_choice_text,
                'correct_answer': correct_text,
                'is_correct': is_correct 
            })
        
        context = {
            'correct_count': correct_count,
            'total_questions': total_questions,
            'detailed_results': detailed_results, 
            'duration_time': duration_string,  # 新增：把格式化好的時間丟給前端
        }
        return render(request, 'quiz/result.html', context)
        
    questions = Question.objects.all()
    return render(request, 'quiz/quiz.html', {'questions': questions})