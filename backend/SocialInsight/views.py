from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import QandA, Messages, Scores, Session, Profile
from .modules import generate_question_and_model_answer, generate_radar_chart, score_to_deviation, calculate_gpt_score
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
    # 未完了のセッションがある場合、それを再利用
    session = Session.objects.filter(user=request.user, is_completed=False).first()

    if not session:
        # 新しいセッションを作成
        session = Session.objects.create(user=request.user)

    # 現在のセッションをセッションストレージに保存
    request.session['current_session_id'] = session.pk

    return redirect('question_view')

import random  # random が必要な場合は忘れずにインポート

@login_required
def question_view(request):
    session_id = request.session.get('current_session_id')

    # セッションが存在しない場合、新しいセッションを作成
    if not session_id:
        return redirect('start_diagnosis')

    try:
        session = Session.objects.get(id=session_id, user=request.user)
    except Session.DoesNotExist:
        return redirect('start_diagnosis')

    answered_count = QandA.objects.filter(user=request.user, session=session).count()

    if answered_count >= 20:
        session.is_completed = True
        session.save()
        return redirect('diagnosis_complete')
    
    # POSTリクエスト時の処理
    if request.method == 'POST':
        if "cancel" in request.POST:
            if answered_count == 0:
                # 一問目の場合はセッションを削除し、セッションストレージから current_session_id を除去してホームへ
                session.delete()
                if 'current_session_id' in request.session:
                    del request.session['current_session_id']
                return redirect('home')
            else:
                # すでに回答がある場合はキャンセルフラグを立てて診断完了ページへ
                session.is_completed = True
                session.is_canceled = True
                session.save()
                return redirect('diagnosis_complete')

        user_answer = request.POST.get('user_answer')
        question_text = request.POST.get('question_text')
        model_answer = request.POST.get('model_answer')
        attribute = request.POST.get('attribute')

        QandA.objects.create(
            user=request.user,
            question_text=question_text,
            model_answer=model_answer,
            user_answer=user_answer,
            attribute=attribute,
            session=session
        )

        return redirect('question_view')

    else:
        answered_attributes = QandA.objects.filter(user=request.user, session=session).values_list('attribute', flat=True)
        all_attributes = [field[0] for field in ATTRIBUTE_CHOICES]
        remaining_attributes = list(set(all_attributes) - set(answered_attributes))

        if remaining_attributes:
            attribute = remaining_attributes[0]
        else:
            attribute = random.choice(all_attributes)

        user_status = request.user.profile.get_status_display()
        has_part_time_job = request.user.profile.has_part_time_job
        
        # 問題文を生成
        question_text, model_answer = generate_question_and_model_answer(attribute, user_status, has_part_time_job)

        context = {
            'question_text': question_text,
            'model_answer': model_answer,
            'attribute': attribute,
            'answered_count': answered_count + 1
        }
        return render(request, 'SocialInsight/question_form.html', context)



# 診断完了
@login_required
def diagnosis_complete(request):
    session_id = request.session.get('current_session_id')

    if not session_id:
        # セッションが存在しない場合、診断開始ページにリダイレクト
        return redirect('start_diagnosis')

    try:
        # 現在のセッションを取得
        session = Session.objects.get(id=session_id, user=request.user)
    except Session.DoesNotExist:
        # セッションが見つからない場合、新しいセッションにリダイレクト
        return redirect('start_diagnosis')

    # 完了ページに表示するデータを準備
    context = {
        'session_id': session_id,
    }

    return render(request, 'SocialInsight/diagnosis_complete.html', context)


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
    sessions_data = []
    sessions = Session.objects.filter(user=request.user).distinct()
    selected_session_id = request.GET.get('session_id')

    # 各セッションの偏差値を計算し、結果をまとめる
    for session in sessions:
        try:
            is_canceled = bool(session.is_canceled)
            deviation_values, user_scores = score_to_deviation(request.user, session.session_id, is_canceled)
            sessions_data.append({
                'id': session.session_id,
                'deviation_value': deviation_values['total']
            })
        except ValueError as e:
            logger.warning(f"セッション {session.session_id} のデータ取得失敗: {e}")
            continue

    if selected_session_id:
        try:
            selected_session_id = int(selected_session_id)
            selected_session = Session.objects.get(session_id=selected_session_id, user=request.user)
            deviation_values, user_scores = score_to_deviation(request.user, selected_session.session_id, is_canceled)

            # レーダーチャートを生成
            image_buffer = generate_radar_chart(request.user, selected_session.session_id)

            # スコアデータを構築
            score_data = [
                {
                    'field': field[1],
                    'score': getattr(user_scores, field[0], 0),  # スコアが存在しない場合に備える
                    'deviation': deviation_values.get(field[0], 0)  # 偏差値が存在しない場合に備える
                }
                for field in ATTRIBUTE_CHOICES if field[0] != 'total'
            ]

            # 合計スコアと合計偏差値
            total_score = user_scores.total
            total_deviation_value = deviation_values['total']

            # 強みと改善点の抽出
            positive_z_scores = [
                (attribute, z_score) for attribute, z_score in deviation_values.items()
                if z_score >= 50 and attribute != 'total'
            ]
            negative_z_scores = [
                (attribute, z_score) for attribute, z_score in deviation_values.items()
                if z_score < 50 and attribute != 'total'
            ]

            strengths = get_messages_by_category(positive_z_scores, 'strength', is_positive=True)
            improvements = get_messages_by_category(negative_z_scores, 'improvement', is_positive=False)

            return render(request, 'SocialInsight/check_result.html', {
                'sessions': sessions_data,
                'session_id': selected_session_id,
                'image_path': image_buffer,
                'score_data': score_data,
                'total_score': total_score,
                'total_deviation_value': total_deviation_value,
                'strengths': strengths,
                'improvements': improvements
            })
        except (ValueError, Session.DoesNotExist) as e:
            logger.error(f"セッションの取得に失敗: {e}")
            return HttpResponse("無効なセッションIDです。", status=400)

    # セッションIDが指定されていない場合のレスポンス
    return render(request, 'SocialInsight/check_result.html', {
        'sessions': sessions_data,
        'session_id': None
    })


@login_required
def radar_chart_image(request, session_id):
    image_buffer = generate_radar_chart(request.user, int(session_id))
    return HttpResponse(image_buffer, content_type='image/png')

@login_required
def answer_list_view(request, session_id=None):

    if request.method == 'POST':
        session_id = request.POST.get('session_id')

    if session_id:    
        answer_lists = QandA.objects.filter(session_id=session_id, user=request.user)
    else:
        answer_lists = []

    return render(request, 'SocialInsight/answer_list.html', {'answer_lists': answer_lists})


@login_required
def get_gpt_scores(request, session_id):
    qanda_records = QandA.objects.filter(session_id=session_id, user=request.user)

    attribute_scores = {}

    for record in qanda_records:
        gpt_result = calculate_gpt_score(record.model_answer, record.user_answer, record.attribute)

        if record.attribute not in attribute_scores:
            attribute_scores[record.attribute] = []

        attribute_scores[record.attribute].append(gpt_result["avg_score"])

    average_scores = {attribute: sum(scores) / len(scores) for attribute, scores in attribute_scores.items()}

    new_scores = {
        'empathy': average_scores.get('empathy', 0),
        'organization': average_scores.get('organization', 0),
        'visioning': average_scores.get('visioning', 0),
        'influence': average_scores.get('influence', 0),
        'inspiration': average_scores.get('inspiration', 0),
        'team': average_scores.get('team', 0),
        'perseverance': average_scores.get('perseverance', 0),
        'total': sum(average_scores.values()),
    }

    Scores.create_new_score(user=request.user, new_scores=new_scores, qanda_session=qanda_records.first().session)

    return render(request, 'SocialInsight/result_scores.html', {
        'session_id': session_id,
        'average_scores': average_scores
    })
