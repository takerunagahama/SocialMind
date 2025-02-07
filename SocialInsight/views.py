from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import QandA, Messages, Scores, Session
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




@login_required
def question_view(request):
    session_id = request.session.get('current_session_id')

    # セッションが存在しない場合、新しいセッションを作成
    if not session_id:
        # セッションが失われた場合、診断開始にリダイレクト
        return redirect('start_diagnosis')

    try:
        # セッションIDに対応するSessionインスタンスを取得
        session = Session.objects.get(id=session_id, user=request.user)
    except Session.DoesNotExist:
        # セッションが見つからない場合、診断開始ページにリダイレクト
        return redirect('start_diagnosis')

    # current_session_id でのユーザーの回答数を取得
    answered_count = QandA.objects.filter(user=request.user, session=session).count()

    # 20問に達したらセッションを完了状態にし、診断完了ページにリダイレクト
    if answered_count >= 20:
        session.is_completed = True
        session.save()
        return redirect('diagnosis_complete')

    if request.method == 'POST':
        # 中断ボタンが押された場合
        if "cancel" in request.POST:
            session.is_completed = True  # セッションを完了状態に
            session.save()
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
            session=session
        )

        return redirect('question_view')

    else:
        # ユーザーに対してまだ出題していない属性を取得
        answered_attributes = QandA.objects.filter(user=request.user, session=session).values_list('attribute', flat=True)
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
    sessions = Session.objects.distinct()  # 全セッションを取得

    # 各セッションの偏差値を計算し、結果をまとめる
    for session in sessions:
        try:
            deviation_values, user_scores = score_to_deviation(session.session_id)
            sessions_data.append({
                'id': session.session_id,
                'deviation_value': deviation_values['total']
            })
        except ValueError as e:
            logger.warning(f"セッション {session.session_id} のデータ取得失敗: {e}")
            continue

    # 選択されたセッションIDを取得
    selected_session_id = request.GET.get('session_id')

    if selected_session_id:
        try:
            selected_session_id = int(selected_session_id)  # セッションIDを整数に変換
            selected_session = Session.objects.get(session_id=selected_session_id)
            deviation_values, user_scores = score_to_deviation(selected_session.session_id)

            # レーダーチャートを生成
            image_buffer = generate_radar_chart(selected_session.session_id)

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


@login_required
<<<<<<< Updated upstream
def get_bert_scores(request, session_id):
    qanda_records = QandA.objects.filter(session_id=session_id)
=======
def get_gpt_scores(request, session_id):
    qanda_records = QandA.objects.filter(session_id=session_id, user=request.user)
>>>>>>> Stashed changes

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
