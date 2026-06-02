import random
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required  
from django.contrib import messages 
from .models import Question, Choice, QuizRecord
from datetime import datetime


def register_view(request):
    """ 註冊帳號 """
    if request.method == 'POST':
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        
        if User.objects.filter(username=u_name).exists():
            messages.error(request, "此帳號已被註冊！")
            return render(request, 'quiz/register.html')
            
        user = User.objects.create_user(username=u_name, password=p_word)
        login(request, user)  
        messages.success(request, "註冊成功！歡迎加入測驗系統")
        return redirect('index')
        
    return render(request, 'quiz/register.html')


def login_view(request):
    """ 登入系統 """
    if request.method == 'POST':
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        
        user = authenticate(request, username=u_name, password=p_word)
        if user is not None:
            login(request, user)
            messages.success(request, "登入成功！")
            return redirect('index')
        else:
            messages.error(request, "帳號或密碼錯誤，請重試。")
            return render(request, 'quiz/login.html')
            
    return render(request, 'quiz/login.html')


def logout_view(request):
    """ 登出系統 """
    logout(request)
    messages.success(request, "您已成功登出！")
    return redirect('index')


def index(request):
    """
    首頁 View：顯示選題畫面、錯題、歷史歷程，以及【全球排行榜】
    """
    wrong_ids = request.session.get('wrong_question_ids', [])
    wrong_count = len(wrong_ids)
    
    my_history = []
    leaderboard_5 = []
    leaderboard_10 = []
    leaderboard_15 = []
    

    if request.user.is_authenticated:
        my_history = QuizRecord.objects.filter(user=request.user).order_by('-created_at')
        
    leaderboard_5 = QuizRecord.objects.filter(total_questions=5).order_by('-score_percent', 'duration')[:5]
    leaderboard_10 = QuizRecord.objects.filter(total_questions=10).order_by('-score_percent', 'duration')[:5]
    leaderboard_15 = QuizRecord.objects.filter(total_questions=15).order_by('-score_percent', 'duration')[:5]
    
    context = {
        'wrong_count': wrong_count,
        'my_history': my_history,
        'leaderboard_5': leaderboard_5,
        'leaderboard_10': leaderboard_10,
        'leaderboard_15': leaderboard_15,
    }
    return render(request, 'quiz/index.html', context)


@login_required(login_url='login') 
def quiz_home(request):
    """ 測驗題目頁面（代碼不變） """
    try:
        num_questions_to_get = int(request.GET.get('num', 15))
    except (ValueError, TypeError):
        num_questions_to_get = 15
    
    wrong_ids = request.session.get('wrong_question_ids', [])
    num_wrong_to_pick = min(len(wrong_ids), num_questions_to_get)
    chosen_wrong_ids = random.sample(wrong_ids, num_wrong_to_pick) if wrong_ids else []
    
    wrong_questions = list(Question.objects.filter(id__in=chosen_wrong_ids))
    num_remain = num_questions_to_get - len(wrong_questions)
    remain_questions = []
    if num_remain > 0:
        remain_queryset = Question.objects.exclude(id__in=chosen_wrong_ids).order_by('?')[:num_remain]
        remain_questions = list(remain_queryset)
    
    final_questions = wrong_questions + remain_questions
    random.shuffle(final_questions)
    request.session['current_quiz_ids'] = [q.id for q in final_questions]
    
    for q in final_questions:
        choices_list = list(q.choices.all())
        random.shuffle(choices_list)
        q.random_choices = choices_list
    
    return render(request, 'quiz/quiz.html', {'questions': final_questions})


@login_required(login_url='login')
def calculate_score(request):
    """ 交卷批改分數頁面（💡 改動：支援加入題目解析） """
    if request.method == 'POST':
        correct_count = 0
        detailed_results = [] 
        current_wrong_set = set()

        raw_seconds = request.POST.get('user_duration', '0')
        try:
            total_seconds = int(raw_seconds)
            mins = total_seconds // 60
            secs = total_seconds % 60
            duration_string = f"{mins:02d}:{secs:02d}"
        except ValueError:
            duration_string = "00:00"

        submitted_question_ids = request.session.get('current_quiz_ids', [])
        if not submitted_question_ids:
            questions = Question.objects.all()
        else:
            questions_map = {q.id: q for q in Question.objects.filter(id__in=submitted_question_ids)}
            questions = [questions_map[qid] for qid in submitted_question_ids if qid in questions_map]
            
        total_questions = len(questions)

        for index, q in enumerate(questions, start=1):
            user_choice_id = (
                request.POST.get(f'q{q.id}') or 
                request.POST.get(f'q{index}') or 
                request.POST.get(f'question_{index}') or
                request.POST.get(f'question_{q.id}')
            )
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
                except (Choice.DoesNotExist, ValueError):
                    pass
            
            if not is_correct:
                current_wrong_set.add(q.id)
            
            detailed_results.append({
                'number': index,
                'content': q.content,
                'user_answer': user_choice_text,
                'correct_answer': correct_text,
                'is_correct': is_correct,
                'explanation': q.explanation  
            })
        
        request.session['wrong_question_ids'] = list(current_wrong_set)
        
        score_percent = int((correct_count / total_questions) * 100) if total_questions > 0 else 0
        
        QuizRecord.objects.create(
            user=request.user, 
            total_questions=total_questions,
            correct_count=correct_count,
            score_percent=score_percent,
            duration=duration_string
        )
        
        context = {
            'correct_count': correct_count,
            'total_questions': total_questions,
            'detailed_results': detailed_results, 
            'duration_time': duration_string,
        }
        return render(request, 'quiz/result.html', context)
        
    return redirect('index')