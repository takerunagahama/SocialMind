import numpy as np
from SocialInsight.models import QandA, Scores, Session

ATTRIBUTE_CHOICES = [
    ('empathy', '共感力'),
    ('organization', '組織理解'),
    ('influence', '影響力'),
    ('visioning', 'ビジョニング'),
    ('team', 'チームワーク力'),
    ('inspiration', '啓発力'),
    ('perseverance', '忍耐力'),
    ('total', '合計点'),
]

def score_to_deviation(user, session_id, is_canceled):
    # Session のデータ取得
    session = Session.objects.filter(session_id=session_id, user=user).first()
    if not session:
        raise ValueError(f"指定したセッションID {session_id} が見つかりません")

    # QandA データ取得（回答済みの数を確認）
    qanda_sessions = QandA.objects.filter(session=session)
    if not qanda_sessions.exists():
        raise ValueError(f"指定したセッションID {session_id} に関連する QandA が見つかりません")

    answered_count = qanda_sessions.count()  # 回答済みの数

    # Scores データ取得
    user_scores = Scores.objects.filter(qanda_session=session, user=user).first()
    if not user_scores:
        raise ValueError(f"指定したセッションID {session_id} に関連するスコアが見つかりません")

    # すべてのスコアを取得
    all_scores = Scores.objects.all()
    if not all_scores.exists():
        raise ValueError('スコアデータが存在しません')

    # 偏差値計算の準備
    score_fields = [field[0] for field in ATTRIBUTE_CHOICES]
    score_data = {field: [getattr(score, field) for score in all_scores] for field in score_fields}

    score_stats = {
        field: {'mean': np.mean(scores), 'std': np.std(scores)}
        for field, scores in score_data.items()
    }

    # スコアの補正処理（is_canceled が True の場合）
    if is_canceled:
        corrected_scores = {}

        # 忍耐力スコアの補正
        perseverance_score = getattr(user_scores, 'perseverance', 50)  # ない場合はデフォルト50
        corrected_scores['perseverance'] = perseverance_score * 0.9

        # 回答済みスコアの平均を算出
        answered_scores = [
            getattr(user_scores, field, None) for field in score_fields
            if getattr(user_scores, field, None) is not None and getattr(user_scores, field) > 0
        ]
        answered_avg = np.mean(answered_scores) if answered_scores else 50

        # 補正係数 α の決定
        if answered_count >= 10:
            alpha = 0.6  # 10問以上なら 0.5～0.7 の範囲
        elif answered_count <= 3:
            alpha = 0.2  # 3問以下なら 0.2
        else:
            alpha = 0.2 + (answered_count - 3) * (0.6 - 0.2) / (10 - 3)  # 線形補間

        # 未回答のスコア補正（忍耐力以外）
        for field in score_fields:
            if field == 'perseverance':
                continue

            existing_score = getattr(user_scores, field, 0)
            if existing_score == 0:  # 未回答の場合のみ補正
                corrected_scores[field] = 50 * (1 - alpha) + answered_avg * alpha
            else:
                corrected_scores[field] = existing_score

        # 補正後のスコアで user_scores を更新
        for field in score_fields:
            setattr(user_scores, field, corrected_scores[field])
        user_scores.save()
    else:
        # キャンセルされていない場合は元のスコアを使用
        corrected_scores = {field: getattr(user_scores, field) for field in score_fields}

    # 偏差値計算
    deviation_values = {}
    for field in score_fields:
        user_score_value = corrected_scores[field]
        mean = score_stats[field]['mean']
        std = score_stats[field]['std']

        deviation_value = 50 if std == 0 else 50 + 10 * (user_score_value - mean) / std
        deviation_values[field] = deviation_value

    return deviation_values, user_scores
