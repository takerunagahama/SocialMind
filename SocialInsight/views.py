from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import QandA, Messages, Session
from .modules import generate_question_and_model_answer, generate_radar_chart, score_to_deviation
import logging
import random

logger = logging.getLogger(__name__)

ATTRIBUTE_CHOICES = [
    ('empathy', '共感力'),
    ('organization', '組織理解'),
    ('influence', '影響力'),
    ('visioning', 'ビジョニング'),
    ('team', 'チームワーク力'),
    ('inspiration', '啓発力'),
    ('perseverance', '忍耐力'),
]

@login_required
def start_diagnosis_view(request):
    session, created = Session.objects.get_or_create(user=request.user)

    if not created:
        session.session_id += 1
        session.save()
    else:
        session.session_id = 1
        session.save()

    request.session['current_session_id'] = session.session_id

    return redirect('question_view')

@login_required
def question_view(request):
    session_id = request.session.get('current_session_id')

    # current_session_idでのユーザーの回答数を取得
    answered_count = QandA.objects.filter(user=request.user, session_id=session_id).count()

    # 20問に達していたら、診断完了ページにリダイレクト
    if answered_count >= 20:
        return redirect('diagnosis_complete')

    if request.method == 'POST':
        # 中断ボタンが押されたとき
        if "canceled" in request.POST:
            return redirect('diagnosis_complete')

        # ユーザーの回答を取得
        user_answer = request.POST.get('user_answer')
        question_text = request.POST.get('question_text')
        model_answer = request.POST.get('model_answer')
        attribute = request.POST.get('attribute')

        # QandAモデルに保存
        QandA.objects.create(
            user=request.user,
            question_text=question_text,
            model_answer=model_answer,
            user_answer=user_answer,
            attribute=attribute,
            session_id=session_id
        )

        return redirect('question_view')

    else:
        # ユーザーに対してまだ出題していない属性を取得
        answered_attributes = QandA.objects.filter(user=request.user).values_list('attribute', flat=True)
        all_attributes = [field[0] for field in ATTRIBUTE_CHOICES]
        remaining_attributes = list(set(all_attributes) - set(answered_attributes))

        if remaining_attributes:
            attribute = remaining_attributes[0]  # まだ出題されていない属性を使う
        else:
            attribute = random.choice(all_attributes)  # 全て出題した後はランダムに選ぶ

        # 問題文を生成
        question_text, model_answer = generate_question_and_model_answer(attribute)

        context = {
            'question_text': question_text,
            'model_answer': model_answer,
            'attribute': attribute,
            'answered_count': answered_count
        }

        return render(request, 'SocialInsight/question_form.html', context)


# 診断完了
@login_required
def diagnosis_complete(request):
    return render(request, 'SocialInsight/diagnosis_complete.html')

def get_messages_by_category(attribute_scores, category, is_positive=True, limit=2):
    if is_positive:
        sorted_scores = sorted(attribute_scores, key=lambda x: x[1], reverse=True)[:limit]
    else:
        sorted_scores = sorted(attribute_scores, key=lambda x: x[1])[:limit]

    messages = []
    
    for attribute, _ in sorted_scores:
        attribute_messages = Messages.objects.filter(attribute=attribute, category=category)[:limit]
        
        for message in attribute_messages:
            messages.append({
                'attribute': dict(ATTRIBUTE_CHOICES).get(attribute),
                'message': message.message,
                'training_name': message.training_name,
                'training_content': message.training_content
            })
    
    return messages
        
@login_required
def check_result(request):
    sessions = []
    session_ids = QandA.objects.values_list('session_id', flat=True).distinct()
    
    for session_id in session_ids:
        deviation_values, user_scores = score_to_deviation(session_id)
        sessions.append({
            'id': session_id,
            'deviation_value': deviation_values['total']
        })

    selected_session_id = request.GET.get('session_id')

    if selected_session_id:
        # 偏差値とスコアを取得
        deviation_values, user_scores = score_to_deviation(int(selected_session_id))

        # レーダーチャート画像を生成
        image_buffer = generate_radar_chart(int(selected_session_id))

        score_data = [
            {
                'field': field[1],
                'score': getattr(user_scores, field[0]),
                'deviation': deviation_values[field[0]]
            }
            for field in ATTRIBUTE_CHOICES if field[0] != 'total'
        ]

        total_score = user_scores.total
        total_deviation_value = deviation_values['total']

        positive_z_scores = [(attribute, z_score) for attribute, z_score in deviation_values.items() if z_score >= 50 and attribute != 'total']
        negative_z_scores = [(attribute, z_score) for attribute, z_score in deviation_values.items() if z_score < 50 and attribute != 'total']

        logger.debug(f"Positive Z Scores: {positive_z_scores}")

        strengths = get_messages_by_category(positive_z_scores or deviation_values.items(), 'strength', is_positive=True)
        improvements = get_messages_by_category(negative_z_scores or deviation_values.items(), 'improvement', is_positive=False)

        return render(request, 'SocialInsight/check_result.html', {
            'sessions': sessions,
            'session_id': selected_session_id,
            'image_path': image_buffer,
            'score_data': score_data,
            'total_score': total_score,
            'total_deviation_value': total_deviation_value,
            'strengths': strengths,
            'improvements': improvements
        })

    return render(request, 'SocialInsight/check_result.html', {
        'sessions': sessions,
        'session_id': selected_session_id
    })

@login_required
def radar_chart_image(request, session_id):
    image_buffer = generate_radar_chart(int(session_id))
    return HttpResponse(image_buffer, content_type='image/png')

@login_required
def answer_list_view(request, session_id=None):

    if request.method == 'POST':
        session_id = request.POST.get('session_id')

    if session_id:    
        answer_lists = QandA.objects.filter(session_id = session_id)
    else:
        answer_lists = []

    return render(request, 'SocialInsight/answer_list.html', {'answer_lists': answer_lists})