from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import QandA
from .text_generation import generate_question_and_model_answer
from .visualization import generate_radar_chart

ATTRIBUTE_CHOICES = [
    'empathy', 'organization', 'visioning', 'influence',
    'inspiration', 'team', 'perseverance'
]

@login_required
def start_diagnosis_view(request):
    session_id = Qand.objects.filter(user=request.user).count() + 1
    request.session['current_session_id'] = session_id
    
    return redirect('question_view')

@login_required
def question_view(request):
    if request.method == 'POST':
        # ユーザーの回答を取得
        user_answer = request.POST.get('user_answer')
        question_text = request.POST.get('question_text')
        model_answer = request.POST.get('model_answer')
        attribute = request.POST.get('attribute')
        
        # QandAモデルに保存
        QandA.objects.create(
            user = request.user,
            question_text = question_text,
            model_answer = model_answer,
            user_answer = user_answer,
            attribute = attribute,
            session_id = request.session.get('current_session_id', 1)
        )

        return redirect('question_view')

    else:
        # ユーザーに対してまだ出題していない属性を取得
        answered_attributes = QandA.objects.filter(user=request.user).values_list('attribute', flat=True)
        remaining_attributes = list(set(ATTRIBUTE_CHOICES) - set(answered_attributes))

        if remaining_attributes:
            attribute = remaining_attributes[0]
        else:
            attribute = random.choice(ATTRIBUTE_CHOICES)

        # 問題文を生成
        question_text, model_answer = generate_question_and_model_answer(attribute)

        context = {
            'question_text': question_text,
            'model_answer': model_answer,
            'attribute': attribute
        }

        return render(request, 'SocialInsight/question_form.html', context)

@login_required
def check_result(request):
    sessions = QandA.objects.values_list('session_id', flat=True).distinct()
    selected_session_id = request.GET.get('session_id')

    if selected_session_id:
        image_buffer = generate_radar_chart(int(selected_session_id))
        return render(request, 'SocialInsight/check_result.html', {'sessions': sessions, 'session_id': selected_session_id, 'image_path': image_buffer})

    return render(request, 'SocialInsight/check_result.html', {'sessions': sessions, 'session_id': selected_session_id})


@login_required
def radar_chart_image(request, session_id):
    image_buffer = generate_radar_chart(int(session_id))
    return HttpResponse(image_buffer, content_type='image/png')